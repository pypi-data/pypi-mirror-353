"""Live Scan Grub Menu."""

__version__ = "0.0.1"

import os
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import lsgm
import rwx.arg
import rwx.fs
import rwx.grub
import rwx.ps

CHARSET = 'UTF-8'

PGP = 'git@marc.beninca.link'

MODULES = (
    ('regexp'),
    ('memdisk', 'tar'),
    ('search'),
    ('part_gpt', 'part_msdos'),
    ('btrfs', 'ext2', 'fat', 'iso9660', 'udf'),
    ('exfat', 'hfs', 'hfspluscomp', 'ntfscomp'),
    ('linux', 'loopback', 'squash4'),
#
    ('at_keyboard', 'keylayouts', 'keystatus', 'read'),
    ('halt', 'reboot'),
    ('all_video', 'videoinfo'),
    ('gfxterm_background', 'jpeg', 'png', 'tga'),
#
    ('date', 'echo', 'eval', 'help', 'sleep', 'test', 'true'),
    ('cpuid', 'lspci'),
    ('cat', 'configfile', 'loadenv', 'progress', 'testspeed'),
    ('hashsum', 'gcry_sha512', 'gcry_sha256'),
    ('pgp', 'gcry_dsa', 'gcry_rsa'),
)


def build(esp_root: str, data_uuid: str=None) -> None:
    esp_uuid = rwx.fs.get_path_uuid(esp_root)
    #
    memdisk_root = os.path.join(esp_root, 'memdisk')
    efi_root = os.path.join(esp_root, 'efi')
    efi_directory = os.path.join(efi_root, 'boot')
    bios_root = os.path.join(esp_root, 'bios')
    grub_root = os.path.join(esp_root, 'grub')
    grub_env = os.path.join(esp_root, 'grub.env')
    #
    print(f'''
esp_root: {esp_root}
data_uuid: {data_uuid}
↓
esp_uuid: {esp_uuid}
↓
memdisk_root: {memdisk_root}
efi_root: {efi_root}
efi_directory: {efi_directory}
bios_root: {bios_root}
grub_root: {grub_root}
grub_env: {grub_env}
''', end=str())
    #
    memdisk_directory = os.path.join(memdisk_root, 'boot', 'grub')
    memdisk_file = os.path.join(memdisk_directory, 'grub.cfg')
    memdisk_archive = os.path.join(memdisk_root, 'boot.tar')
    #
    print(f'''
memdisk_directory: {memdisk_directory}
memdisk_file: {memdisk_file}
memdisk_archive: {memdisk_archive}
''', end=str())
    #
    rwx.fs.wipe(memdisk_root)
    rwx.fs.make_directory(memdisk_directory)
    rwx.fs.empty_file(memdisk_file)
    # EFI
    rwx.fs.wipe(efi_root)
    rwx.fs.make_directory(efi_directory)
    # BIOS
    rwx.fs.wipe(bios_root)
    rwx.fs.make_directory(bios_root)
    #
    rwx.fs.wipe(memdisk_root)
    # GRUB
    rwx.fs.wipe(grub_root)
    # GRUB / environment
    rwx.fs.write(grub_env,
        rwx.grub.ENV_HEADER.ljust(rwx.grub.ENV_BYTES, rwx.grub.ENV_COMMENT))


def __main__():
    esp()


def main(main_file: str) -> None:
    function, _ = os.path.splitext(os.path.basename(main_file))
    getattr(lsgm, function)()


def doc():
    root = os.path.dirname(__file__)
    file = os.path.join(root, 'todo')
    subprocess.run([
        'dot',
        f'{file}.gv',
        '-T', 'svg',
        '-o', f'{file}.svg',
    ])


def esp():
    command, args = rwx.arg.split()
    if args:
        data, *args = args
    else:
        data = None
    project_file = os.path.realpath(__file__)
    project_root = os.path.dirname(project_file)
    parent_root, project_name = os.path.split(project_root)
    #
    print(f'''
command: {command}
data: {data}
args: {args}
↓
project_file: {project_file}
project_root: {project_root}
parent_root: {parent_root}
project_name: {project_name}
''', end=str())
    #
    if project_name:
        build(parent_root, data_uuid=data)
