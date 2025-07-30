# GRUB

## Devices

* (crypto?)
* (hd?)
* (hd?,*)
* (lvm/*)
* (md/*)
* (memdisk)

## Commands

### arm

* xen_hypervisor
* xen_module

### bios

* drivemap
* sendkey

### x86_64-efi-signed

#### denied

##### lockdown

* acpi
* badram
* cutmem

##### secure boot

* all_functional_test
* appleloader
* backtrace
* blocklist
* cbmemc
* cmp
* coreboot_boottime
* crc
* date
* eval
* extract_legacy_entries_configfile
* extract_legacy_entries_source
* extract_syslinux_entries_configfile
* extract_syslinux_entries_source
* fakebios
* file
* fix_video
* functional_test
* gptsync
* hashsum
* hdparm
* hello
* hexdump
* hexdump_random
* inb
* initrd16
* inl
* inw
* keymap
* kfreebsd
* kfreebsd_loadenv
* kfreebsd_module
* kfreebsd_module_elf
* knetbsd
* knetbsd_module
* knetbsd_module_elf
* kopenbsd
* kopenbsd_ramdisk
* legacy_check_password
* legacy_configfile
* legacy_initrd
* legacy_initrd_nounzip
* legacy_kernel
* legacy_password
* legacy_source
* linux16
* loadbios
* lsacpi
* lscoreboot
* lsmmap
* lspci
* macppcbless
* mactelbless
* md5sum
* module
* module2
* multiboot
* multiboot2
* nativedisk
* outb
* outl
* outw
* parttool
* password
* pcidump
* rdmsr
* read
* read_byte
* read_dword
* read_word
* setpci
* sha1sum
* sha256sum
* sha512sum
* syslinux_configfile
* syslinux_source
* test_blockarg
* testload
* testspeed
* time
* tr
* usb
* videoinfo
* videotest
* write_byte
* write_dword
* write_word
* wrmsr
* xnu_devprop_load
* xnu_kernel
* xnu_kernel64
* xnu_kext
* xnu_kextdir
* xnu_mkext
* xnu_ramdisk
* xnu_resume
* xnu_splash
* xnu_uuid

#### allowed

* background_color
* submenu
* terminal_input
* terminfo

##### unused

* .
* authenticate
* boot
* break
* cat
* clear
* continue
* cpuid
* distrust
* dump
* extract_entries_configfile
* extract_entries_source
* gettext
* help
* initrdefi
* insmod
* keystatus
* linuxefi
* lsefi
* lsefimmap
* lsefisystab
* lsfonts
* lsmod
* lssal
* net_add_addr
* net_add_dns
* net_add_route
* net_bootp
* net_bootp6
* net_del_addr
* net_del_dns
* net_del_route
* net_dhcp
* net_get_dhcp_option
* net_ipv6_autoconf
* net_ls_addr
* net_ls_cards
* net_ls_dns
* net_ls_routes
* net_nslookup
* normal
* password_pbkdf2
* play
* rmmod
* search.file
* search.fs_label
* search.fs_uuid
* serial
* set
* test
* zfs-bootfs
* zfsinfo
* zfskey

##### used

* [
* background_image
* chainloader
* configfile
* cryptomount
* echo
* exit
* export
* false
* fwsetup
* halt
* initrd
* linux
* list_env
* list_trusted
* load_env
* loadfont
* loopback
* ls
* menuentry
* normal_exit
* probe
* reboot
* regexp
* return
* save_env
* search
* setparams
* shift
* sleep
* smbios
* source
* terminal_output
* true
* trust
* unset
* verify_detached

## Variables

* biosnum
* icondir
* net_default_interface
* pxe_blksize
* pxe_default_gateway
* superusers

* config_directory
* config_file

* debug
* default
* fallback
* gfxmode
* gfxpayload
* gfxterm_font
* menu_color_highlight
* menu_color_normal
* theme
* timeout
* timeout_style

### Function

* ?

### Persistent

* feature_200_final
* feature_all_video_module
* feature_chainloader_bpb
* feature_default_font_path
* feature_menuentry_id
* feature_menuentry_options
* feature_nativedisk_cmd
* feature_ntldr
* feature_platform_search_hint
* feature_timeout_style
* net_default_ip
* net_default_mac
* net_default_server
* pxe_default_server
* secondary_locale_dir

* check_signatures
* chosen
* cmdpath
  * (hd?,*)/efi/boot/bootx64.efi
  * (hd?)
* color_highlight
* color_normal
* grub_cpu
* grub_platform
* lang
* locale_dir
* pager
* prefix
* root

#### x86_64-efi-signed

* lockdown
* shim_lock
