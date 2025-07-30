function scan {
    if [ "${1}" ] ; then
        paths="${1}/*"
    else
        regexp --set default '(\(.*\))' "${cmdpath}"
        paths='(*)'
    fi
    for path in ${paths} ; do
        if [ "${1}" ] ; then
            regexp --set tmp '.*/(.*)' "${path}"
        else
            if [ "${path}" == "${default}" ] ; then
                tmp="→ ${path}"
            else
                tmp="  ${path}"
            fi
            probe_set "${path}"
            tmp="${tmp}${probe_entry}"
        fi
        if [ "${tmp}" != '*' ] ; then
            if [ -d "${path}" ] ; then
                menuentry "${tmp} →" "${path}" --id "${path}" {
                    scan="${2}"
                    menu
                }
            else
                menuentry "${tmp}" {
                    nop
                }
            fi
        fi
        if [ ! "${1}" ] ; then
            if [ "${probe_fs}" == 'fat' ] ; then
                if [ -f "${path}/efi/boot/bootx64.efi" ] ; then
                    menuentry '   efi/boot/bootx64.efi →' "${path}" {
                        chainloader "${2}/efi/boot/bootx64.efi"
                    }
                fi
            elif [ "${probe_fs}" ] ; then
                if [ -d "${path}/boot/bash" ] ; then
                    for x in ${path}/boot/bash/* ; do
                        if [ -f "${x}/gui/filesystem.squashfs" ] ; then
                            regexp --set y '\(.*\)/(.*)' "${x}/gui"
                            menuentry "   ${y} →" {
                                nop
                            }
                        fi
                    done
                fi
            fi
            probe_unset
        fi
    done
}
