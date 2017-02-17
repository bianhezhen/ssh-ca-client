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
    ssh_ca_client.ssh
    ~~~~~~~~~~~~~~~~~~~~

    Implements all interactions with local ssh client
"""

import os
import subprocess


class SSH(object):

    @staticmethod
    def agent_identities_loaded():
        """ Determine number of currently loaded identities
            ssh just throws loaded identities at remote server and will fail after 5 identities
        """

        identity_count = 0
        loaded_identities = subprocess.Popen(["ssh-add", "-l"], stdout=subprocess.PIPE)

        if loaded_identities.returncode == 2:
            raise SystemError("Unable to access SSH keychain. Please run 'eval `ssh-agent -s`'")

        with loaded_identities.stdout as identities:
            for identity in identities:
                identity_count += 1

        return identity_count

    @staticmethod
    def remove_keypair_from_sshagent(keypair_name):
        """ Remove ssh keypair from sshagent

        :param keypair_name: Name of keypair to be unloaded from sshagent

        """

        user_home = os.path.expanduser("~")
        private_key_file = "{}/.ssh/{}_rsa".format(user_home, keypair_name)

        try:
            subprocess.check_call(["ssh-add",
                                   "-d", private_key_file],
                                  stdout=open(os.devnull, "w"),
                                  stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as err:
            if err.returncode == 2:
                raise SystemError("Unable to edit SSH keychain. Please run 'eval `ssh-agent -s`'")

    @staticmethod
    def add_keypair_to_sshagent(keypair_name):
        """ Add ssh keypair to sshagent

        :param keypair_name: Name of keypair to be loaded by sshagent

        """

        user_home = os.path.expanduser("~")
        private_key_file = "{}/.ssh/{}_rsa".format(user_home, keypair_name)

        try:
            subprocess.check_call(["ssh-add", private_key_file])

        except subprocess.CalledProcessError as err:
            if err.returncode == 2:
                raise SystemError("Unable to edit SSH keychain. Please run 'eval `ssh-agent -s`'")

    @staticmethod
    def create_keypair(keypair_name):
        """ Create ssh keypair

        :param keypair_name: Name of keypair to be created

        """

        user_home = os.path.expanduser("~")
        public_key_file = "{}/.ssh/{}_rsa.pub".format(user_home, keypair_name)
        public_key_name = "{}/.ssh/{}_rsa".format(user_home, keypair_name)

        if not os.path.isfile(public_key_file):
            subprocess.call(["ssh-keygen",
                             "-f", public_key_name,
                             "-q",
                             "-P", ""])
