# -*- coding: utf-8 -*-

# Copyright 2016 Commerce Technologies, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    ssh_ca_client.server
    ~~~~~~~~~~~~~~~~~~~~

    Implements all CA server API calls
"""

import json
import requests
import os
from .ssh import SSH
from .config import Config


class Server(object):

    def __init__(self):
        self.is_healthy()

    @staticmethod
    def is_healthy():
        """ Make a call to the CA server (base_url) and bomb out if it fails or unsupported api version """

        try:
            response = requests.get(Config.BASE_URL)
            json_response = json.loads(response.text)

        except requests.exceptions.ConnectionError:
            raise IOError("Unable to access CA server URL <{}>".format(Config.BASE_URL))

        if "version" in json_response:
            if json_response["version"] != Config.API_VERSION:
                raise ValueError("Client version issue.  Please update your client code.")

        else:
            raise IOError("Server response issue.  Please contact your administrator.")

    @staticmethod
    def list_roles(username):
        """ Print all roles user has access to

        :param username: if username is not provided currently logged in username is used

        """

        request_url = "{}/list/roles?user={}".format(Config.BASE_URL, username)
        response = requests.get(request_url)

        json_response = json.loads(response.text)

        if json_response["error"]:
            print("")
            print(json_response["message"])
            print("")
        else:
            if len(json_response["payload"]) == 0:
                print("")
                print("currently have no roles assigned to you.")
                print("")
            else:
                for role in json_response['payload']:
                    print("")
                    print("Role:               {}".format(role['name']))
                    print("Description:        {}".format(role['description']))
                    print("Allowed Principals: {}".format(role['allowed_principals']))
                    print("Allowed CAs:        {}".format(role['allowed_cas']))
                    print("")

    @staticmethod
    def list_cas():
        """ Print all active certificate authorities """

        request_url = "{}/list/cas".format(Config.BASE_URL)
        response = requests.get(request_url)

        json_response = json.loads(response.text)

        if json_response["error"]:
            print("")
            print(json_response["message"])
            print("")
        else:
            for ca in json_response["payload"]:
                print("")
                print("CA name:        {}".format(ca['name']))
                print("Max duration:   {}".format(ca['max_duration']))
                print("")

    @staticmethod
    def get_public_key(ca_name):
        """ Get CA public key

        :param ca_name: Name of CA provided by CA server

        """

        request_url = '{}/get/{}'.format(Config.BASE_URL, ca_name)
        response = requests.get(request_url)

        json_response = json.loads(response.text)

        if json_response["error"]:
            print("")
            print(json_response["message"])
            print("")

        else:
            print("")
            print("Update /etc/ssh/ sshd_config on remote host to include:")
            print("")
            print("    TrustedUserCAKeys /etc/ssh/user_ca.pub")
            print("")
            print("Add the following to /etc/ssh/user_ca.pub:")
            print("")
            print("    ssh-rsa {}".format(json_response['payload']))
            print("")
            print("You can login if the principal your cert is singed with exists on the remote host.")
            print("")

    @staticmethod
    def sign_request(ca, username, password):
        """ Grab users ssh public key and requests signing
            If no key pair exists one will be created to match name of ca
            The retrieved cert will override anything existing in users .ssh folder

        :param ca: Name of CA provided by CA server
        :param username: username used in the http post authenticating user
        :param password: password used in the http post authenticating user

        """

        user_home = os.path.expanduser("~")

        ssh_home = "{}/.ssh".format(user_home)
        if not os.path.exists(ssh_home):
            os.makedirs(ssh_home)

        private_key_file = "{}/.ssh/{}_rsa".format(user_home, ca)
        public_key_file = "{}/.ssh/{}_rsa.pub".format(user_home, ca)
        cert_file = "{}/.ssh/{}_rsa-cert.pub".format(user_home, ca)

        if not os.path.isfile(public_key_file):
            SSH.create_keypair(ca)
            print("SSH public key created for {}.".format(ca))

        request_url = "{}/sign?ca={}".format(Config.BASE_URL, ca)
        files = {"file": open(public_key_file)}
        response = requests.post(request_url, files=files, auth=(username, password))

        json_response = json.loads(response.text)
        if json_response["error"]:
            print(json_response["message"])

        else:
            # Must remove previous cert from ssh-agent before adding the new one
            # Not doing this first results in multiple disassociated entries for
            # previous certs

            SSH.remove_keypair_from_sshagent(ca)

            file_handle = open(cert_file, "w")
            file_handle.write(json_response["payload"])
            file_handle.close()

            print("")
            print("{} updated".format(file_handle.name))
            print("")

            if SSH.agent_identities_loaded() > 3:

                print("ERROR: Identity could not be loaded for ssh-agent")
                print("ssh-agent should not exceed 5 identities")
                print("Use ssh with -i to use new key or remove unneeded identities from ssh-agent using ssh-add -d")
                print("")

            else:
                SSH.add_keypair_to_sshagent(ca)

                print("Identity loaded for current session but ssh-agent will not persist identities on reboot")
                print("")
                print("If using bash you can add the following command to your .bash_profile")
                print("ssh-add {}".format(private_key_file))
                print("")
