#! /usr/bin/env bash
FILE="$(realpath "${BASH_SOURCE[0]}")"
cd "$(dirname "${FILE}")" ||
	exit

ROOT='root/msys2'

rm s/msys/*.tar
rm i/mingw/mingw64/*.tar

rm -fr "${ROOT}/msys/x86_64"
mv -i s/msys "${ROOT}/msys/x86_64"

rm -fr "${ROOT}/mingw"
mv -i i/mingw "${ROOT}/"

rmdir s i
