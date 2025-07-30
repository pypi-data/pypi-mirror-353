function sys_set {
    sys_unset
    smbios --set sys_manufacturer --type  1 --get-string  4
    smbios --set sys_product      --type  1 --get-string  5
    smbios --set sys_serial       --type  1 --get-string  7
    smbios --set sys_uuid         --type  1 --get-uuid    8
    smbios --set sys_cpu          --type  4 --get-string 16
    smbios --set sys_ram_max_kb   --type 16 --get-dword   7
    smbios --set sys_ram_max_nb   --type 16 --get-word   13
    smbios --set sys_ram_kb       --type 19 --get-dword   8
    smbios --set sys_ram_nb       --type 19 --get-byte   14
}

function sys_unset {
    unset sys_manufacturer
    unset sys_product
    unset sys_serial
    unset sys_uuid
    unset sys_cpu
    unset sys_ram_max_kb
    unset sys_ram_max_nb
    unset sys_ram_kb
    unset sys_ram_nb
}
