#! /usr/bin/env sh

file="$(readlink --canonicalize-existing "${0}")"
root="$(dirname "${file}")"
root="${root}/root/py/cpypy"

path="${root}/download-metadata.json"
url="https://github.com/astral-sh/uv/raw/refs/heads/main/crates/uv-python/download-metadata.json"

rm --force --recursive "${root}"
mkdir --parents "${root}"
wget --continue --output-document "${path}" "${url}" 2>/dev/null
echo
echo "${path}"
cat "${path}"

for url in $(jq -r ".. | objects | .url?" "${path}" |
	grep "\(/20250311/\|/pypy3.11-v7.3.19\)" |
	grep --invert-match "debug" |
	grep --invert-match "\(armv7\|ppc64le\|s390x\)" |
	grep --invert-match "\(apple-darwin\|macos\|win64\|windows-msvc\)"); do
	case "$(basename "${url}")" in
	cpython-3.13* | \
	cpython-3.12* | \
	cpython-3.11* | \
	cpython-3.10* | \
	pypy3.11*)
		file="$(basename "${url}" | sed "s|%2B|+|g")"
		dir="$(dirname "${url}")"
		date="$(basename "${dir}")"
		path="${root}/${date}"
		mkdir --parents "${path}"
		wget --continue --output-document "${path}/${file}" "${url}"
		;;
	*) ;;
	esac
done
