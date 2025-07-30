#! /usr/bin/python3 -B

import os
import shutil
import subprocess

ALGO_NAME = "SHA256"
VAR_NAME = "var"


if __name__ == "__main__":
    root_directory = os.path.dirname(os.path.realpath(__file__))
    root_directory = os.path.join(root_directory, 'deb.apt-mirror')
    hashes_file = os.path.join(root_directory, VAR_NAME, ALGO_NAME)
    with open(hashes_file) as f:
        lines = f.readlines()
    hashes_by_names = {}
    for line in lines:
        hash, name = line.split()
        hashes_by_names[name] = hash
    files = len(hashes_by_names)
    i = 1
    ko = 0
    os.chdir(os.path.join(root_directory, "mirror"))
    command = ALGO_NAME.lower() + 'sum "{}"'
    for name, hash in sorted(hashes_by_names.items()):
        columns, rows = shutil.get_terminal_size()
        progress = " ".join([str(files), str(ko), str(i), ""])
        available = columns - len(progress) - 1
        short_name = name[-available:]
        padding = " " * (available- len(short_name))
        print("\r", progress, short_name, padding, sep="", end="", flush=True)
        output = subprocess.getoutput(command.format(name))
        h, *_ = output.split()
        if h != hash:
            print()
            try:
                os.remove(name)
            except:
                pass
            ko += 1
        i += 1
    print()
    print(ko)
