MODULES=(
'regexp'
'memdisk' 'tar'
'search'
'part_gpt' 'part_msdos'
'lvm' 'mdraid1x'
'btrfs' 'ext2' 'iso9660' 'udf'
'exfat' 'fat' 'hfs' 'hfspluscomp' 'ntfscomp'
'linux' 'loopback' 'squash4'
#
# 'at_keyboard' 'cpuid' 'keylayouts' 'lspci' ← not in arm64-efi
'keystatus' 'read'
'halt' 'reboot'
'all_video' 'videoinfo'
'gfxterm_background' 'jpeg' 'png' 'tga'
#
'date' 'echo' 'eval' 'help' 'sleep' 'test' 'true'
'cat' 'configfile' 'loadenv' 'progress' 'testspeed'
'hashsum' 'gcry_sha256' 'gcry_sha512'
'pgp' 'gcry_dsa' 'gcry_rsa'
)

MODULES_BIOS=(
'biosdisk'
'ntldr'
)
