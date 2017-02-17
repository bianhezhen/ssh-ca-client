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
    ssh_ca_client.config
    ~~~~~~~~~~~~~~~~~~~~

    Get configuration from user if none exists otherwise load from file
"""

import json
import os.path
try:
    import __builtin__
    input = getattr(__builtin__, 'raw_input')
except (ImportError, AttributeError):
    pass


class Config(object):

    API_VERSION = "1.01"
    CONFIG_FILE = "config.json"
    DEFAULT_CA = ""
    BASE_URL = ""
    CONFIG_PATH = ""

    def __init__(self):
        Config.CONFIG_PATH = Config.get_config_path()

        if not Config.load_configuration():
            print("Failed to load configuration from {}".format(Config.CONFIG_PATH))
            Config.get_configuration()
            Config.save_configuration()

    @classmethod
    def get_config_path(cls):
        """ Get full path of configuration """

        home_path = os.path.expanduser("~")
        config_path = "{}/.ca-client/{}".format(home_path, Config.CONFIG_FILE)

        return config_path

    @classmethod
    def load_configuration(cls):
        """ Load configuration from file """

        if os.path.isfile(Config.CONFIG_PATH):
            with open(Config.CONFIG_PATH, 'r') as config_file:
                try:
                    loaded_config = json.loads(config_file.read())
                except ValueError:
                    print("Configuration file is corrupted")
                    return False

                try:
                    Config.BASE_URL = loaded_config["BASE_URL"]
                    Config.DEFAULT_CA = loaded_config["DEFAULT_CA"]
                except KeyError:
                    print("Missing required configuration")
                    return False
        else:
            return False

        return True

    @classmethod
    def save_configuration(cls):
        """ Write active configuration to file """

        config_dir = os.path.dirname(Config.CONFIG_PATH)

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        config = {"BASE_URL": Config.BASE_URL,
                  "DEFAULT_CA": Config.DEFAULT_CA}

        with open(Config.CONFIG_PATH, "w") as config_file:
            config_file.write(json.dumps(config))

    @classmethod
    def get_configuration(cls):
        """ Get configuration from user """

        base_url = input("Enter FQDN of CA Server:")

        # Default to HTTPS but allow user to override protocol
        # HTTP should only be used for testing
        if len(base_url.split("//")) > 1:
            Config.BASE_URL = base_url
        else:
            Config.BASE_URL = "https://{}".format(base_url)

        default_ca = input("Enter name of default CA:")
        Config.DEFAULT_CA = default_ca
