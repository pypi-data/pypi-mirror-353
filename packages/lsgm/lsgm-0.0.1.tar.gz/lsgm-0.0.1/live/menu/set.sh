env_init
menu_init

default='split'

grub_list_const 'menu'
grub_split 'menu'
grub_list_vars 'menu'
grub_split 'menu'
grub_list_xtra 'menu'
menu_split 'split'
menu_swap "check_squashfs | ${check_squashfs}" 'check_squashfs' 'enforce' 'no'
menu_swap "     live_from | ${live_from}" 'live_from' 'ram' 'media'
menuentry "         pause | ${pause}" { menu 'pause' }
menu_split
menuentry "esp: ${esp}" { nop }
menuentry "env_mod: ${env_mod}" { nop }
menuentry "pager: ${pager}" { nop }
