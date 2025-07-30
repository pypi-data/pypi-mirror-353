env_init
menu_init

default='scan'

menuentry ' scan →' --id 'scan' { menu 'scan' }
menuentry '↑ gfx →' { menu 'gfx' }
menuentry '↑ env →' { menu 'env' }
menuentry '↑ set →' { menu 'set' }
menuentry '↑ cmd →' { menu 'cmd' }
menu_split
submenu 'submenu with env →' {
    env_init
    menuentry 'configfile' { configfile "${live}/configfile.sh" }
    menu_swap "check_squashfs | ${check_squashfs}" \
        'check_squashfs' 'enforce' 'no'
}
submenu 'submenu without env →' {
    menuentry 'configfile' { configfile "${live}/configfile.sh" }
    menu_swap "check_squashfs | ${check_squashfs}" \
        'check_squashfs' 'enforce' 'no'
}
menu_split
menuentry 'static →' { menu 'static' }
