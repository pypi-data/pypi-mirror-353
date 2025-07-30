env_init
menu_init

menuentry 'exit normal' { normal_exit }
menuentry 'exit grub' { exit }
menu_split
menuentry 'setup firmware' { fwsetup }
menu_split
menuentry 'reboot' { reboot }
menuentry 'halt' { halt }
