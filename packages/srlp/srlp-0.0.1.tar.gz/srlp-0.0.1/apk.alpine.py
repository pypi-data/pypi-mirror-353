#! /usr/bin/env python3

import os
import subprocess

ROOT = 'rsync://rsync.kyberorg.fi/alpine'
ROOT = 'rsync://alpine.mirror.wearetriple.com/alpine'
ROOT = 'rsync://mirrors.dotsrc.org/alpine'
ROOT = 'rsync://uk.alpinelinux.org/alpine'
ARCH = 'x86_64'
VERSIONS = [
    'v3.21',
]

TARGETS = {
    'v3.21': [
        'releases',
        'main',
        'community',
    ],
}


def sync(source, target):
    args = ['rsync',
            '--archive',
            # '--checksum',
            '--delete-before',
            # '--dry-run',
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
    root = os.path.join(root, 'root', 'apk', 'alpine')
    sources = []
    for version in VERSIONS:
        for target in TARGETS[version]:
            sources.append(os.path.join(version, target, ARCH) + os.sep)
    for source in sources:
        target = os.path.join(root, source)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        sync(os.path.join(ROOT, source), target)


if __name__ == '__main__':
    main()
