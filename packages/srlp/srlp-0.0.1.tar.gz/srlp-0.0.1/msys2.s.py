#! /usr/bin/python3 -B

import os
import requests
import shutil
import subprocess
import sys
import tarfile

ARCHITECTURE = 'x86_64'
REPOSITORY = 'https://repo.msys2.org'


def download(url, file):
    print(file)
    response = requests.get(f'{url}/{file}')
    open(file, 'bw').write(response.content)


def download_subrepo(root, directory, prefix):
    path = os.path.join(root, directory)
    print()
    print(path)
    os.makedirs(path)
    os.chdir(path)
    url = f'{REPOSITORY}/{directory}/{ARCHITECTURE}'
    for suffix in ['files', 'db']:
        archive = f'{prefix}.{suffix}'
        download(url, f'{archive}.sig')
        download(url, f'{archive}')
    subprocess.run(['unzstd',
                    f'{archive}',
                    '-o', f'{archive}.tar'])
    archive = tarfile.open(f'{archive}.tar')
    packages = [m for m in archive.getmembers() if m.isfile()]
    names = []
    for package in packages:
        desc = archive.extractfile(package)
        desc.readline()
        names.append(desc.readline().strip().decode('u8'))
    archive.close()
    for name in names:
        archive = f'{name}'
        signature = f'{archive}.sig'
        download(url, f'{archive}.sig')
        download(url, f'{archive}')


def main():
    _, directory, *_ = sys.argv
    output_directory = os.path.realpath(directory)
    print(output_directory)
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)
    download_subrepo(output_directory, 'msys', 'msys')
#    download_subrepo(output_directory, 'mingw', 'mingw64')


if __name__ == '__main__':
    main()
