# -*- coding: utf-8 -*-
import pathlib
import configparser
from pprint import pprint
import sys

default_lsl_api_cfg = {
    "ports": {
        "MulticastPort": "16571",
        "BasePort": "16572",
        "PortRange": "32",
        "IPv6": "allow",
    },
    "multicast": {
        "ResolveScope": "site",
        "MachineAddresses": "{FF31:113D:6FDD:2C17:A643:FFE2:1BD1:3CD2}",
        "LinkAddresses": "{255.255.255.255, 224.0.0.183, FF02:113D:6FDD:2C17:A643:FFE2:1BD1:3CD2}",
        "SiteAddresses": "{239.255.172.215, FF05:113D:6FDD:2C17:A643:FFE2:1BD1:3CD2}",
        "OrganizationAddresses": "{239.192.172.215, FF08:113D:6FDD:2C17:A643:FFE2:1BD1:3CD2}",
        "GlobalAddresses": "{}",
        "AddressesOverride": "{}",
        "TTLOverride": "-1",
    },
    "lab": {"KnownPeers": "{}", "SessionID": "default"},
}


def get_target_for_lsl_api_cfg(level: str):
    "see https://labstreaminglayer.readthedocs.io/info/lslapicfg.html"
    if level == "system":
        if "win" in sys.platform:
            return pathlib.Path(r"C:\etc\lsl_api\lsl_api.cfg")
        else:
            return pathlib.Path("/etc/lsl_api/lsl_api.cfg")
    elif level == "user":
        if "win" in sys.platform:
            return pathlib.Path(r"~/lsl_api/lsl_api.cfg").expanduser()
        else:
            return pathlib.Path("~/lsl_api/lsl_api.cfg").expanduser()
    elif level == "local":
        return pathlib.Path.cwd() / "lsl_api.cfg"


class Ini:

    ini = configparser.ConfigParser()
    ini.optionxform = str

    def __init__(self, level="user"):
        path = get_target_for_lsl_api_cfg(level)
        self.path = path

    def reset_defaults(self):
        self.ini.read_dict(default_lsl_api_cfg)
        self.write()

    def as_dict(self):
        self.refresh()
        dictionary = {}
        for section in self.ini.sections():
            dictionary[section] = {}
            for option in self.ini.options(section):
                dictionary[section][option] = self.ini.get(section, option)
        return dictionary

    def write(self):
        with open(self.path, "w") as f:
            self.ini.write(f)
        self.refresh()

    def refresh(self):
        self.ini.read(self.path)


# %%


def init_lsl_api_cfg(level: str):
    targetfile = get_target_for_lsl_api_cfg(level)
    targetfile.parent.mkdir(exist_ok=True, parents=True)
    ini = Ini(level)
    ini.reset_defaults()
    print("Created a configuration file at", targetfile)


def print_config(level: str):
    file = get_target_for_lsl_api_cfg(level)
    if file.exists():
        pprint(Ini(level).as_dict())
    else:
        print("No configuration found for this level")

