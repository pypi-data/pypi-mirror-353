function env {
    action="${1}"
    setparams \
    'check_squashfs' \
    'live_from' \
    'pause' \
    'time_out'
    if [ "${action}" == 'load' ] ; then
        load_env \
        --file "${env}" \
        --skip-sig \
        "${@}"
    fi
    if [ "${action}" == 'save' ] ; then
        save_env \
        --file "${env}" \
        "${@}"
    fi
    if [ "${action}" == 'set' ] ; then
        load_env \
        "${@}"
    fi
    unset action
}

function env_apply {
    if [ "${default}" ] ; then
        timeout=${time_out}
    else
        unset timeout
    fi
}

function env_get {
    unset get
    if [ "${1}" == 'check_squashfs' ] ; then get="${check_squashfs}" ; fi
    if [ "${1}" == 'live_from' ] ; then get="${live_from}" ; fi
    if [ "${1}" == 'pause' ] ; then get="${pause}" ; fi
    if [ "${1}" == 'time_out' ] ; then get="${time_out}" ; fi
    if [ ! "${get}" ] ; then false ; fi
}

function env_init {
    grub_init
    sys_set
    env set
    env_mod
    env load
    env_apply
}

function env_list {
    list_env \
    --skip-sig \
    --file "${env}"
}

function env_mod {
    env_mod='---'
    if [ -f "${env}" ] ; then
        env_mod='--x'
        if env 'load' ; then
            env_mod='r-x'
            if env 'save' ; then
                env_mod='rwx'
            fi
        fi
    fi
}
