#! /usr/bin/env bash
[ "${2}" ] || exit 1
FILE="$(realpath "${BASH_SOURCE[0]}")"
SCRIPT="$(basename "${FILE}")"
ROOT="$(dirname "${FILE}")"
PROJECT="$(basename "${ROOT}")"

PGP_PUB="${1}"
ESP_ROOT="${2}"
DATA_ROOT="${3}"

function get_path_mount {
    stat --format '%m' "${1}"
}
function get_mount_uuid {
    findmnt --noheadings --output 'UUID' "${1}"
}
function get_path_uuid {
    local tmp="$(get_path_mount "${1}/")"
    get_mount_uuid "${tmp}"
}
ESP="$(get_path_uuid "${ESP_ROOT}")"
if [ "${DATA_ROOT}" ] ; then
    DATA="$(get_path_uuid "${DATA_ROOT}")"
else
    DATA="${ESP}"
fi

function sign {
    if [ -d "${1}" ] ; then
        local file
        local files
        readarray -t files <<< "$(find "${1}" -type f | sort)"
        echo
        echo "${1}"
        for file in "${files[@]}" ; do
            sign "${file}" "${1}"
        done
    fi
    if [ -f "${1}" ] ; then
        if [ "${2}" ] ; then
            echo "$(realpath --relative-to "${2}" "${1}")"
        else
            echo "${1}"
        fi
        gpg \
        --quiet \
        --default-key "${PGP_PUB}!" \
        --detach-sign \
        "${1}"
    fi
}

# imports ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

source "${ROOT}/${SCRIPT%.*}.mod"

# constants ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

BIOS_BOOT='/usr/lib/grub/i386-pc/boot.img'
COMPRESSION='xz'
GRUB_HEAD='# GRUB Environment Block'
SIGNED_GRUB='/usr/lib/grub/x86_64-efi-signed/grubx64.efi.signed'
SIGNED_SHIM='/usr/lib/shim/shimx64.efi.signed'
SIGNED_ARM_GRUB='/usr/lib/grub/arm64-efi-signed/grubaa64.efi.signed'
ARM_SHIM='/usr/lib/shim/shimaa64.efi.signed'

# variables ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

MEMDISK_ROOT="${ESP_ROOT}/memdisk"
MEMDISK_DIRECTORY="${MEMDISK_ROOT}/grub"
MEMDISK_FILE="${MEMDISK_DIRECTORY}/grub.cfg"
MEMDISK_FONTS="${MEMDISK_DIRECTORY}/fonts"
MEMDISK_ARCHIVE="${MEMDISK_ROOT}/grub.tar"

UEFI_ROOT="${ESP_ROOT}/efi"
UEFI_DIRECTORY="${UEFI_ROOT}/boot"
UEFI_CORE="${UEFI_DIRECTORY}/corex64.efi"
UEFI_FILE="${UEFI_DIRECTORY}/bootx64.efi"
UEFI_GRUB="${UEFI_DIRECTORY}/grubx64.efi"
ARM_CORE="${UEFI_DIRECTORY}/coreaa64.efi"
ARM_FILE="${UEFI_DIRECTORY}/bootaa64.efi"
ARM_GRUB="${UEFI_DIRECTORY}/grubaa64.efi"

BIOS_ROOT="${ESP_ROOT}/bios"
BIOS_FILE="${BIOS_ROOT}/core.img"
BIOS_SETUP="${BIOS_ROOT}/setup.sh"

BOOT_ROOT="${ESP_ROOT}/boot"

GRUB_CFG_SH="${ROOT}/grub.cfg.sh"
GRUB_SHIGNED="${ROOT}/grubx64.efi.signed.sh"

GRUB_ROOT="${BOOT_ROOT}/grub"
GRUB_CFG="${GRUB_ROOT}/grub.cfg"
GRUBENV="${GRUB_ROOT}/grubenv"
GRUB_FONTS="${GRUB_ROOT}/fonts"
GRUB_LOCALES="${GRUB_ROOT}/locale"
GRUB_PUB="${GRUB_ROOT}/grub.pgp"
GRUB_THEMES="${GRUB_ROOT}/themes"

GRUB_ENV="${ESP_ROOT}/grub.env"

LIVE_ROOT="${BOOT_ROOT}/${PROJECT}"

# wipe ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

echo -n "
→ ${BOOT_ROOT}
→ ${MEMDISK_ROOT}
→ ${UEFI_ROOT}
→ ${BIOS_ROOT}
"
rm --force --recursive \
"${BOOT_ROOT}" "${MEMDISK_ROOT}" "${UEFI_ROOT}" "${BIOS_ROOT}"

# memdisk ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

echo -n "
→ ${MEMDISK_FONTS}
"
mkdir --parents "${MEMDISK_FONTS}"

echo -n "
→ ${MEMDISK_FILE}
"
echo "\
echo \"prefix | \${prefix}\"
search --no-floppy --set root --fs-uuid '${ESP}'
prefix=\"(\${root})/boot/grub\"
echo \"prefix | \${prefix}\"
" > "${MEMDISK_FILE}"
echo -n "
↙ ${GRUB_SHIGNED}
↘ ${MEMDISK_FILE}
"
cat "${GRUB_SHIGNED}" >> "${MEMDISK_FILE}"

echo -n "
↙ ${MEMDISK_DIRECTORY}
↘ ${MEMDISK_ARCHIVE}
"
cd "${MEMDISK_DIRECTORY}"
tar --create --auto-compress \
--file "${MEMDISK_ARCHIVE}" 'grub.cfg'
cd -

# uefi ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

echo -n "
→ ${UEFI_DIRECTORY}
"
mkdir --parents "${UEFI_DIRECTORY}"

echo -n "
↙ ${MEMDISK_ARCHIVE}
↘ ${UEFI_FILE}
"
grub-mkimage \
--compress "${COMPRESSION}" \
--memdisk "${MEMDISK_ARCHIVE}" \
--format 'x86_64-efi' \
--output "${UEFI_FILE}" \
--prefix '(memdisk)/' \
"${MODULES[@]}"
echo -n "
↙ ${MEMDISK_ARCHIVE}
↘ ${ARM_FILE}
"
grub-mkimage \
--compress "${COMPRESSION}" \
--memdisk "${MEMDISK_ARCHIVE}" \
--format 'arm64-efi' \
--output "${ARM_FILE}" \
--prefix '(memdisk)/' \
"${MODULES[@]}"

if [ -f "${SIGNED_SHIM}" ] ; then
    echo -n "
↙ ${UEFI_FILE}
↘ ${UEFI_GRUB}
"
    mv "${UEFI_FILE}" "${UEFI_GRUB}"
    echo -n "
↙ ${SIGNED_SHIM}
↘ ${UEFI_FILE}
"
    cp "${SIGNED_SHIM}" "${UEFI_FILE}"
fi
if [ -f "${ARM_SHIM}" ] ; then
    echo -n "
↙ ${ARM_FILE}
↘ ${ARM_GRUB}
"
    mv "${ARM_FILE}" "${ARM_GRUB}"
    echo -n "
↙ ${ARM_SHIM}
↘ ${ARM_FILE}
"
    cp "${ARM_SHIM}" "${ARM_FILE}"
fi

if [ -f "${SIGNED_GRUB}" ] ; then
    echo -n "
↙ ${UEFI_GRUB}
↘ ${UEFI_CORE}
"
    mv "${UEFI_GRUB}" "${UEFI_CORE}"
    echo -n "
↙ ${SIGNED_GRUB}
↘ ${UEFI_GRUB}
"
    cp "${SIGNED_GRUB}" "${UEFI_GRUB}"
fi
if [ -f "${SIGNED_ARM_GRUB}" ] ; then
    echo -n "
↙ ${ARM_GRUB}
↘ ${ARM_CORE}
"
    mv "${ARM_GRUB}" "${ARM_CORE}"
    echo -n "
↙ ${SIGNED_ARM_GRUB}
↘ ${ARM_GRUB}
"
    cp "${SIGNED_ARM_GRUB}" "${ARM_GRUB}"
fi

# bios ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

echo -n "
→ ${BIOS_ROOT}
"
mkdir "${BIOS_ROOT}"

echo -n "
↙ ${BIOS_BOOT}
↘ ${BIOS_ROOT}
"
cp "${BIOS_BOOT}" "${BIOS_ROOT}"

echo -n "
↙ ${MEMDISK_ARCHIVE}
↘ ${BIOS_FILE}
"
grub-mkimage \
--compress "${COMPRESSION}" \
--memdisk "${MEMDISK_ARCHIVE}" \
--format 'i386-pc' \
--output "${BIOS_FILE}" \
--prefix '(memdisk)/' \
"${MODULES[@]}" "${MODULES_BIOS[@]}"

echo -n "
→ ${BIOS_SETUP}
"
echo -n '#! /usr/bin/env bash
FILE="$(realpath "${BASH_SOURCE[0]}")"
DIRECTORY="$(dirname "${FILE}")"

/usr/lib/grub/i386-pc/grub-bios-setup \
--directory "${DIRECTORY}" \
"${1}"
' >> "${BIOS_SETUP}"

# grub ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

echo -n "
→ ${GRUB_ROOT}
"
mkdir --parents "${GRUB_ROOT}"

# grub / cfg ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

echo -n "
↙ ${GRUB_CFG_SH}
↘ ${GRUB_CFG}
"
cp "${GRUB_CFG_SH}" "${GRUB_CFG}"

# grub / env ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

function write_env {
local file="${1}"
local kv="${2}"
local text="${GRUB_HEAD}
${kv}"
    while [ ${#text} -lt 1024 ] ; do
        text="${text}#"
    done
    echo -n "${text}" > "${file}"
}

echo -n "
→ ${GRUBENV}
→ ${GRUB_ENV}
"

write_env "${GRUBENV}" "\
live_name=${PROJECT}
data_uuid=${DATA}
check_squashfs=enforce
live_from=ram
pause=999
time_out=10
"

write_env "${GRUB_ENV}" "\
"

# grub / fonts ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

echo -n "
→ ${GRUB_FONTS}
"
mkdir --parents "${GRUB_FONTS}"
for font in $(find '/usr/share/grub' -type 'f' -name '*.pf2') ; do
    cp "${font}" "${GRUB_FONTS}"
done

# grub / themes ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

if cd '/usr/share/grub/themes' ; then
    echo -n "
→ ${GRUB_THEMES}
"
    mkdir --parents "${GRUB_THEMES}"
    for theme in * ; do
        if [ -f "${theme}/theme.txt" ] ; then
            cp --recursive "${theme}" "${GRUB_THEMES}"
        fi
    done
    cd -
fi

# grub / locales ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

echo -n "
→ ${GRUB_LOCALES}
"
mkdir --parents "${GRUB_LOCALES}"
if cd '/usr/share/locale' ; then
    for locale in * ; do
        file="${locale}/LC_MESSAGES/grub.mo"
        if [ -f "${file}" ] ; then
            cp "${file}" "${GRUB_LOCALES}/${locale}.mo"
        fi
    done
    cd -
fi

# grub / pubkey ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

echo -n "
↙ ${PGP_PUB}
↘ ${GRUB_PUB}
"
gpg --export "${PGP_PUB}" > "${GRUB_PUB}"

# grub / modules ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

for target in 'x86_64-efi' 'i386-pc' 'arm64-efi' ; do
    echo -n "
↙ /usr/lib/grub/${target}
↘ ${GRUB_ROOT}/${target}
"
    if cd "/usr/lib/grub/${target}" ; then
        mkdir --parents "${GRUB_ROOT}/${target}"
        for module in *.lst *.mod ; do
            cp "${module}" "${GRUB_ROOT}/${target}"
        done
        cd -
    fi
done

# project ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

cp --recursive "${ROOT}/live" "${LIVE_ROOT}"

# sign ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

sign "${BIOS_ROOT}"
sign "${UEFI_ROOT}"
sign "${LIVE_ROOT}"
sign "${GRUB_ROOT}"

# display ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

echo
du --human-readable --summarize \
"${BIOS_ROOT}" \
"${UEFI_ROOT}" \
"${LIVE_ROOT}" \
"${GRUB_ROOT}" \
"${ESP_ROOT}/"
echo -n "
 ESP: ${ESP}
DATA: ${DATA}
"

# clean ⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅⋅

rm --force --recursive "${MEMDISK_ROOT}"
