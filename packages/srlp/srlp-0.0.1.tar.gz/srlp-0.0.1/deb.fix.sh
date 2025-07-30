#! /usr/bin/env bash
FILE="$(realpath "${BASH_SOURCE[0]}")"
ROOT="$(dirname "${FILE}")"

ERROR='→ ERROR! ERROR! ERROR! ←'
DISTS=(
	'bookworm' 'bookworm-backports' 'bookworm-updates'
)
MISSING='Contents-all.gz'
SECTIONS=('main' 'non-free-firmware' 'contrib' 'non-free')

DEBIAN_ROOT='debian/dists'
LOCAL_ROOT="${ROOT}/root/deb/debian/${DEBIAN_ROOT}"
REMOTE_ROOT="https://deb.debian.org/${DEBIAN_ROOT}"

for dist in "${DISTS[@]}"; do
	for section in "${SECTIONS[@]}"; do
		cd "${LOCAL_ROOT}/${dist}/${section}" ||
			echo "${ERROR}"
		rm --force "${MISSING}"
		wget "${REMOTE_ROOT}/${dist}/${section}/${MISSING}" &>/dev/null ||
			echo "${ERROR}"
	done
done
