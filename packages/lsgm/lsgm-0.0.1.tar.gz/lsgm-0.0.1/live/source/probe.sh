function probe_set {
    probe_unset
    if [ "${1}" ] ; then
        probe "${1}" --set probe_fs --fs
        probe "${1}" --set probe_fs_uuid --fs-uuid
        probe "${1}" --set probe_label --label
        probe "${1}" --set probe_part_uuid --part-uuid
    fi
    if [ "${probe_label}" ] ; then
        probe_entry="${probe_entry} → ${probe_label}"
    fi
    if [ "${probe_fs}" ] ; then
        probe_entry="${probe_entry} → ${probe_fs}"
    fi
    if [ "${probe_fs_uuid}" ] ; then
        probe_entry="${probe_entry} → ${probe_fs_uuid}"
    fi
}

function probe_unset {
    unset probe_entry
    unset probe_fs
    unset probe_fs_uuid
    unset probe_label
    unset probe_part_uuid
}
