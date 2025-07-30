#! /usr/bin/env python3
"""Mirror local Incus."""

from pathlib import Path
import os

from rwx.fs import make_directory, wipe


ROOT = "https://images.linuxcontainers.org"

IMAGES = f"{ROOT}/images"
META = f"{ROOT}/meta"

STREAMS = f"{META}/simplestreams/v1"

TYPE = (
    "default",
)
TYPES = (
    "default",
    "cloud",
)
ARCHITECTURES_TYPE = {
    "amd64": TYPE,
    "arm64": TYPE,
}
ARCHITECTURES_TYPES = {
    "amd64": TYPES,
    "arm64": TYPES,
}
EL = {
    "9": ARCHITECTURES_TYPES,
    "8": ARCHITECTURES_TYPES,
}


def architectures_type(*versions: str) -> dict:
    return {version: ARCHITECTURES_TYPE for version in versions}


def architectures_types(*versions: str) -> dict:
    return {version: ARCHITECTURES_TYPES for version in versions}


PROFILE = {
    "nixos": architectures_type("24.11"),
    # apk
    "alpine": architectures_types("3.21", "3.20"),
    # deb
    "debian": architectures_types("bookworm", "bullseye"),
    "ubuntu": architectures_types("noble", "jammy"),
    # rpm
    "almalinux": EL,
    "fedora": architectures_types("42", "41"),
    "opensuse": {
        "15.6": ARCHITECTURES_TYPES,
        "15.5": ARCHITECTURES_TYPE,
    },
    "rockylinux": EL,
    # rolling
    "archlinux": {
        "current": {
            "amd64": TYPES,
            "arm64": TYPE,
        },
    },
}


def main() -> None:
    root = Path(__file__).resolve().parent / "root"
    # root path
    root = root / "incus"
    wipe(root)
    make_directory(root)
    # symlink
    (root / "streams").symlink_to(os.sep.join(["meta", "simplestreams"]))
    # meta
    meta = root / "meta"
    # streams
    streams = meta / "simplestreams" / "v1"
    make_directory(streams)
    # images
    streams = root / "images"


if __name__ == "__main__":
    main()
