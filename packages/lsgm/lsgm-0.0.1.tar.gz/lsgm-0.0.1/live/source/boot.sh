function almsquash {
    lmp="${1}"
    sfs='squashfs.img'
    #
    if [ "${check_squashfs}" == 'enforce' ] ; then
        chk="(${data})${lmp}/${sfs}"
        echo 'verify_detached'
        echo "${chk}"
        if ! verify_detached "${chk}" "${chk}.sig" ; then
            grub_pause
            return 1
        fi
    fi
    if [ -f "(${data})${lmp}/vmlinuz" ] ; then
        linux_path="(${data})${lmp}/vmlinuz"
        initrd_path="(${data})${lmp}/initrd.img"
    else
        linux_path="(squash)/vmlinuz"
        initrd_path="(squash)/initrd.img"
        loopback "squash" "${lmp}/${sfs}"
    fi
    #
    echo
    echo 'linux'
    echo "${linux_path}"
    toram=''
    if [ "${live_from}" == 'ram' ] ; then
        toram='rd.live.ram=1'
    fi
    linux \
"${linux_path}" \
elevator='deadline' \
ip='frommedia' \
rd.live.dir="${lmp}" \
rd.live.squashimg="${sfs}" \
"${toram}"
    #
    echo
    echo 'initrd'
    echo "${initrd_path}"
    initrd "${initrd_path}"
}

function debsquash {
    lmp="${1}"
    sfs="filesystem.squashfs"
    #
    if [ "${check_squashfs}" == 'enforce' ] ; then
        chk="(${data})${lmp}/${sfs}"
        echo 'verify_detached'
        echo "${chk}"
        if ! verify_detached "${chk}" "${chk}.sig" ; then
            grub_pause
            return 1
        fi
    fi
    if [ -f "(${data})${lmp}/vmlinuz" ] ; then
        linux_path="(${data})${lmp}/vmlinuz"
        initrd_path="(${data})${lmp}/initrd.img"
    else
        linux_path="(squash)/vmlinuz"
        initrd_path="(squash)/initrd.img"
        loopback "squash" "${lmp}/${sfs}"
    fi
    #
    echo
    echo 'linux'
    echo "${linux_path}"
    toram='toram'
    if [ "${live_from}" == 'ram' ] ; then
        toram="${toram}=${sfs}"
    fi
    linux \
"${linux_path}" \
boot="live" \
elevator="deadline" \
ip="frommedia" \
live-media-path="${lmp}" \
live-media-uuid="${data_uuid}" \
"${toram}"
    #
    echo
    echo 'initrd'
    echo "${initrd_path}"
    initrd "${initrd_path}"
}
function ubusquash {
    lmp="${1}"
    sfs="filesystem.squashfs"
    #
    if [ "${check_squashfs}" == 'enforce' ] ; then
        chk="(${data})${lmp}/${sfs}"
        echo 'verify_detached'
        echo "${chk}"
        if ! verify_detached "${chk}" "${chk}.sig" ; then
            grub_pause
            return 1
        fi
    fi
    if [ -f "(${data})${lmp}/vmlinuz" ] ; then
        linux_path="(${data})${lmp}/vmlinuz"
        initrd_path="(${data})${lmp}/initrd.img"
    else
        linux_path="(squash)/vmlinuz"
        initrd_path="(squash)/initrd.img"
        loopback "squash" "${lmp}/${sfs}"
    fi
    #
    echo
    echo 'linux'
    echo "${linux_path}"
    toram='toram'
    if [ "${live_from}" == 'ram' ] ; then
        toram="${toram}=${sfs}"
    fi
    linux \
"${linux_path}" \
boot="live" \
elevator="deadline" \
live-media-path="${lmp}" \
live-media-uuid="${data_uuid}" \
"${toram}"
    #
    echo
    echo 'initrd'
    echo "${initrd_path}"
    initrd "${initrd_path}"
}
