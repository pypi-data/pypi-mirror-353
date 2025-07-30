#! /usr/bin/env sh

set \
	"pip" \
	"setuptools" \
	"wheel" \
	\
	"uv" \
	\
	"Lektor" \
	"Nikola" \
	"pelican" \
	\
	"hatch" \
	\
	"Sphinx" \
	"sphinx-rtd-theme" \
	\
	"commitizen" \
	"gitlint" \
	"GitPython" \
	\
	"pydoclint" \
	"pylint" \
	"ruff" \
	\
	"pytest" \
	\
	"toml" \
	\
	"twine" \
	\
	"mypy" \
	"pyright" \
	\
	"ruamel.yaml" \
	"PyYAML" \
	"types-PyYAML" \
	\
	"yt-dlp" \
	\
	"ansible" \
	\
	"Cython" \
	"maturin"

file="$(readlink --canonicalize-existing "${0}")"
root="$(dirname "${file}")"
root="${root}/root/py/pypi"
tmp="${root}/tmp"

rm --force --recursive "${root}"

for version in \
"os" \
"python3.13" \
"python3.12" \
"python3.11" \
"python3.10" \
"pypy3.11" \
; do
	export VIRTUAL_ENV="/prj/venv/${version}"
	export OLD_PATH="${PATH}"
	export PATH="${VIRTUAL_ENV}/bin:${PATH}"

	sub="${root}"
	# sub="${root}/${version}"

	python3 -m pip \
		download \
		--dest "${sub}" \
		"${@}"

	export PATH="${OLD_PATH}"
	unset OLD_PATH VIRTUAL_ENV
done

	prefix="Name: "
	for wheel in "${sub}/"*; do
		rm --force --recursive "${tmp}"
		mkdir --parents "${tmp}"
		echo
		echo "${wheel}"
		file="$(basename "${wheel}")"
		case "${file}" in
		*.tar.gz)
			short="${file%.*}"
			short="${short%.*}"
			;;
		*.whl)
			short="${file%.*}"
			;;
		esac
		file_name="$(echo "${short}" | cut -d "-" -f 1)"
		file_version="$(echo "${short}" | cut -d "-" -f 2)"
		case "${file}" in
		*.tar.gz)
			meta_data="${file_name}-${file_version}/${file_name}.egg-info/PKG-INFO"
			if ! tar xf "${wheel}" -C "${tmp}" "${meta_data}"; then
				meta_data="${file_name}-${file_version}/PKG-INFO"
				tar xf "${wheel}" -C "${tmp}" "${meta_data}" || exit
			fi
			;;
		*.whl)
			meta_data="${file_name}-${file_version}.dist-info/METADATA"
			unzip "${wheel}" "${meta_data}" -d "${tmp}" || exit
			;;
		esac
		name="$(grep "${prefix}" "${tmp}/${meta_data}" | sed "s|${prefix}||")"
		echo "${name}"
		name="$(echo "${name}" | tr "[:upper:]" "[:lower:]")"
		name="$(echo "${name}" | tr "." "-")"
		name="$(echo "${name}" | tr "_" "-")"
		name="$(echo "${name}" | tr -d "\r")"
		echo "${name}"
		simple="${sub}/simple/${name}"
		mkdir --parents "${simple}"
		mv -i "${wheel}" "${simple}/"
	done

rm --force --recursive "${tmp}"
