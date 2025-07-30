env_init
menu_init "${env} → ${env_mod}"

menuentry 'list file' {
    env_list
    grub_pause
}
menuentry 'list variables' {
    set
    grub_pause
}
menuentry 'reset defaults' {
    env set
    env save
    env_apply
}
