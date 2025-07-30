#! /usr/bin/env python3

import os
import subprocess

ROOT = 'rsync://mirror.in2p3.fr/pub/epel'
ARCH = 'x86_64'
VERSIONS = [
    '8',
    '9',
]

KEY = 'RPM-GPG-KEY-EPEL'
TARGETS = {
    '8': [
        'Everything',
        # 'Modular',
    ],
    '9': [
        'Everything',
    ],
}


def sync(source, target):
    args = ['rsync',
            '--archive',
            # '--checksum',
            '--delete-before',
            # '--dry-run',
            '--inplace',
            '--no-motd',
            '--partial',
            '--progress',
            '--verbose',
            source,
            target,
            ]
    print()
    print()
    print('←', source)
    print('→', target)
    subprocess.call(args)


def main():
    file = os.path.realpath(__file__)
    root = os.path.dirname(file)
    root = os.path.join(root, 'root', 'rpm', 'epel')
    sources = [KEY]
    for version in VERSIONS:
        sources.append(f'{KEY}-{version}')
        for target in TARGETS[version]:
            sources.append(os.path.join(version, target, ARCH) + os.sep)
    for source in sources:
        target = os.path.join(root, source)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        sync(os.path.join(ROOT, source), target)


if __name__ == '__main__':
    main()
