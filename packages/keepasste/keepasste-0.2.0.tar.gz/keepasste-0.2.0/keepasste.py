import subprocess
import tomllib
import base64
import os.path
import sys
import urllib.parse
import re


def main():
    try:
        pasted = subprocess.check_output(["wl-paste", "--primary"], encoding="utf8")[:-1]
    except subprocess.CalledProcessError:
        print("wl-pasted did't exit correctly")
        sys.exit(1)
    with open(os.path.expanduser("~/.config/keepasste/config.toml"), "rb") as f:
        config = tomllib.load(f)

    key = None
    for fn in (
        lambda pasted: pasted,
        lambda pasted: urllib.parse.urlparse(pasted).netloc,
        lambda pasted: re.sub("/.*", "", pasted),
    ):
        needle = fn(pasted)

        if needle in config["mappings"]:
            key = config["mappings"][needle]
            break

        sld_tld = ".".join(needle.split(".")[-2:])
        if sld_tld in config["mappings"]:
            key = config["mappings"][sld_tld]
            break

    if key is None:
        print(f"Cannot find {pasted} in ~/.config/keepasste/config.toml")
        sys.exit(1)

    p = subprocess.Popen(
        [
            "keepassxc-cli",
            "show",
            "-s",
            "-a",
            sys.argv[1],
            config["database"]["filename"],
            key,
        ],
        encoding="utf8",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    value = p.communicate(
        base64.b64decode(config["database"]["password"]).decode("utf8")
    )[0][:-1]

    subprocess.check_call(
        ["sudo", "/usr/bin/injectinput", value.replace("\\", "\\\\") + "\\r"]
    )
