#! /usr/bin/python3 -B

import os
import shutil
import subprocess

LIST_DIRECTORY = "deb.list.d"
LIST_FILE = "deb.list"
SKELETON = "skel"
VARIABLE = "var"


if __name__ == "__main__":
    # directories
    root_directory = os.path.dirname(os.path.realpath(__file__))
    command_directory = os.path.join(root_directory, 'deb.apt-mirror')
    # files
    lines = ['set base_path "{}"'.format(command_directory) + os.linesep]
    os.chdir(root_directory)
    for directory, _, files in os.walk(LIST_DIRECTORY):
        for file in files:
            with open(os.path.join(directory, file)) as f:
                lines.append(os.linesep)
                lines.extend(f.readlines())
    # write
    os.chdir(root_directory)
    string = "".join(lines)
    print(string, end="")
    with open(LIST_FILE, "w") as file:
        file.write(string)
    # wipe
    os.chdir(command_directory)
    shutil.rmtree(SKELETON, ignore_errors=True)
    shutil.rmtree(VARIABLE, ignore_errors=True)
    # run
    os.chdir(root_directory)
    subprocess.call([os.path.join(root_directory, "deb.fork"), LIST_FILE])
    os.remove(LIST_FILE)
    # wipe
    os.chdir(command_directory)
    shutil.rmtree(SKELETON, ignore_errors=True)
