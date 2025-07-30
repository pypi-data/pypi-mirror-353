function grub_fix {
    unset cmdroot
    regexp --set cmdroot '^\((.*)\)' "${cmdpath}"
    if [ "${cmdroot}" != "${root}" ] ; then
        echo -n "\
                 |*${cmdpath}
"
        if [ -d "(${cmdroot})/boot/grub/${grub_cpu}-${grub_platform}" ] ; then
            prefix="(${cmdroot})/boot/grub"
            root="${cmdroot}"
        fi
    fi
    unset cmdroot
    check_signatures='enforce'
    trust --skip-sig "${prefix}/grub.pgp"
}

function grub_init {
    load_env \
    'live_name' 'data_uuid'
    #
    regexp --set esp '^\((.*)\)' "${prefix}"
    #
    env="(${esp})/grub.env"
    load_env \
    --skip-sig \
    --file "${env}" \
    'pause'
    #
    live="(${esp})/boot/${live_name}"
    #
    search --no-floppy --set data \
    --fs-uuid "${data_uuid}"
}

function grub_list_const {
    target="${1}"
    setparams \
"    cpu-platform | ${grub_cpu}-${grub_platform}" \
"         cmdpath | ${cmdpath}"
    for entry in "${@}" ; do
        if [ "${target}" == 'menu' ] ; then
            menuentry "${entry}" { nop }
        else
            echo "${entry}"
        fi
    done
    unset entry
    unset target
}

function grub_list_info {
    if [ -f '/.disk/info' -o -f '/.disk/mini-info' ] ; then
        for f in '/.disk/info' '/.disk/mini-info' ; do
            echo -n "\
                 |"
            if [ -f "${f}" ] ; then
                echo -n '*'
            else
                echo -n ' '
            fi
            echo "(${root})${f}"
        done
        unset f
    fi
}

function grub_list_vars {
    target="${1}"
    setparams \
"            root |  ${root}" \
"          prefix | ${prefix}" \
"check_signatures | ${check_signatures}"
    for entry in "${@}" ; do
        if [ "${target}" == 'menu' ] ; then
            menuentry "${entry}" { nop }
        else
            echo "${entry}"
        fi
    done
    unset entry
    unset target
    list_trusted
}

function grub_list_xtra {
    target="${1}"
    setparams \
"             env | ${env}" \
"            live | ${live}" \
"            data |  ${data}"
    for entry in "${@}" ; do
        if [ "${target}" == 'menu' ] ; then
            menuentry "${entry}" { nop }
        else
            echo "${entry}"
        fi
    done
    unset entry
    unset target
}

function grub_main {
    echo '---'
    ls
    grub_list_const
    grub_split
    if [ ! "${data}" ] ; then
        grub_list_info
        grub_list_vars
        grub_split
        #
        grub_fix
        grub_init
        for file in ${live}/source/*.sh ; do
            source "${file}"
        done
        unset file
        source "${live}/menu/main.sh"
    fi
    grub_list_vars
    grub_list_xtra
    grub_split
    grub_pause
}

function grub_pause {
    echo -n "\
          escape | "
    sleep \
    --interruptible \
    --verbose \
    "${pause}"
}

function grub_split {
    target="${1}"
    setparams \
'                ---'
    if [ "${target}" == 'menu' ] ; then
        menuentry "${1}" { nop }
    else
        echo "${1}"
    fi
}

grub_main
