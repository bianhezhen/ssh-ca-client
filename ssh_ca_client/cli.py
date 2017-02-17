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
    ssh_ca_client.cli
    ~~~~~~~~~~~~~~~~~~~~

    Implements client interface
"""

import argparse
import getpass
import sys
from .server import Server
from .config import Config


def parse_args():
    """ Get some arguments """

    parser = argparse.ArgumentParser(
        description="Tool to sign your public SSH key")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--sign",
                       help="certificate signing request", metavar="CA")
    parser.add_argument("-u", "--user",
                        help="optional username for signing request")
    group.add_argument("-r", "--list-roles",
                       help="list my authorized roles", action="store_true")
    group.add_argument("-c", "--list-cas",
                       help="list available CAs", action="store_true")
    group.add_argument("-k", "--get-key",
                       help="list public key for CA", metavar="CA")
    parser.add_argument("-p", "--password",
                        help="optional password for signing request")

    return parser.parse_args()


def get_password(username):

    """ Request password from user used to authenticate to CA server

    :param username: Pass in the username form pretty printing

    """
    password = getpass.getpass("Please enter password for {}:".format(username))
    return password


def main():

    args = parse_args()

    config = Config()
    print("Loading configuration from {}".format(Config.CONFIG_PATH))

    try:
        ca_server = Server()

    except(IOError, ValueError) as error:
        print("")
        print(error)
        print("")
        sys.exit(1)

    password = None

    # What username are we working with
    if args.user:
        username = args.user
    else:
        username = getpass.getuser()

    # Allow password to be provided as a parameter
    if args.password:
        password = args.password

    if args.list_roles:

        ca_server.list_roles(username)

    elif args.list_cas:
        ca_server.list_cas()

    elif args.get_key:
        ca_server.get_public_key(args.get_key)

    else:

        if args.sign:
            ca = args.sign
        else:
            ca = Config.DEFAULT_CA

        if password is None:
            password = get_password(username)

        try:
            ca_server.sign_request(ca, username, password)

        except SystemError as message:
            print("")
            print(message)
            print("")
            sys.exit(1)
