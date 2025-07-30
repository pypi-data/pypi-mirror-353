function menu {
    if [ "${1}" ] ; then
        menu_load "${1}"
    else
        export menu
        menu_load "${menu}"
    fi
}

function menu_color {
    setparams \
    'black'     'blue'          'green'       'cyan' \
    'red'       'magenta'       'brown'       'light-gray' \
    'dark-gray' 'light-blue'    'light-green' 'light-cyan' \
    'light-red' 'light-magenta' 'yellow'      'white'
    for color in "${@}" ; do
        menu_item "${color}"
    done
    unset color
}

function menu_exit {
    env save
    menu
}

function menu_init {
    if [ "${menu}" ] ; then
        if [ "${1}" ] ; then
            menuentry "→ ${menu} → ${1}" { nop }
        else
            menuentry "→ ${menu}" { nop }
        fi
        menu_split
        default=2
        if env_get "${menu}" ; then
            default="_${get}"
            unset get
        fi
    fi
}

function menu_item {
    if [ "${1}" ] ; then
        if [ "${2}" ] ; then
            entry="${2}"
        else
            entry="${1}"
        fi
        menuentry "${entry}" "${1}" "${menu}" --id "_${1}" {
            ${3}="${2}"
            menu_exit
        }
        unset entry
    fi
}

function menu_load {
    menu="${1}"
    export menu
    configfile "${live}/menu/${menu}.sh"
}

function menu_split {
    if [ "${1}" ] ; then
        menuentry '' --id "${1}" { nop }
    else
        menuentry '' { nop }
    fi
}

function menu_swap {
    if [ "${4}" ] ; then
        menuentry "${1}" "${2}" "${3}" "${4}" {
            if env_get "${2}" ; then
                if [ "${get}" == "${3}" ] ; then
                    ${2}="${4}"
                else
                    ${2}="${3}"
                fi
                unset get
                menu_exit
            fi
        }
    fi
}
