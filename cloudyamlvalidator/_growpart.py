def growpart(self, section):
    if self._internal_test:
        return

    LV_SCRIPT = "$CGEDIR/scripts/include/extend_logical_volumes.sh"

    # First drive validation
    first_drive_pv = self._run_shell("source %s; get_first_drive_partition" % LV_SCRIPT)

    # Check that 'root_size_gib' + 'log_size_gib' < total size of first drive
    pv_total_size_GiB = float(self._run_shell("source %s; get_physical_volume_total_size %s" %
                                              (LV_SCRIPT, first_drive_pv))) / 1024

    root_desired_size_GiB = section.get("root_size_gib", 0)
    log_desired_size_GiB = section.get("log_size_gib", 0)
    lv_total_size_GiB = root_desired_size_GiB + log_desired_size_GiB

    if lv_total_size_GiB > pv_total_size_GiB:
        self._raise_error("Invalid input for first drive (%s): The sum of 'root_size_gib' and 'log_size_gib' (%.2f GiB)"
                          " must be <= physical volume's total size (%.2f GiB)" %
                          (first_drive_pv, lv_total_size_GiB, pv_total_size_GiB))

    # We only allow to increase the current sizes of root and log logical volumes
    if "root_size_gib" in section:
        root_current_size_GiB = float(self._run_shell(
            "lvdisplay --unit g /dev/vg_splat/lv_current | grep 'LV Size' | awk '{print $3}'"))
        if root_desired_size_GiB <= root_current_size_GiB:
            self._raise_error("Invalid input for 'root_size_gib' parameter: The desired size for root "
                              "partition (%.2f GiB) must be > current size of root partition (%.2f GiB)" %
                              (root_desired_size_GiB, root_current_size_GiB))

    if "log_size_gib" in section:
        log_current_size_GiB = float(self._run_shell(
            "lvdisplay --unit g /dev/vg_splat/lv_log | grep 'LV Size' | awk '{print $3}'"))
        if log_desired_size_GiB <= log_current_size_GiB:
            self._raise_error("Invalid input for 'log_size_gib' parameter: The desired size for log "
                              "partition (%.2f GiB) must be > current size of log partition (%.2f GiB)" %
                              (log_desired_size_GiB, log_current_size_GiB))

    # Additional drives validation
    if "additional_drives" in section and section["additional_drives"] is not None:
        # Drives list validation
        additional_drives = section["additional_drives"]
        additional_drives_sys = self._run_shell("source %s; get_additional_drives_partitions" % LV_SCRIPT).split()
        if len(additional_drives) > len(additional_drives_sys):
            self._raise_error("Invalid input for 'additional_drives': list's length (%d) must be <= number of additional"
                              " drives in the system (%d)" % (len(additional_drives), len(additional_drives_sys)))

        # Check 'root_percent' + 'log_percent' <= 100
        for index in range(len(additional_drives)):
            root_percent = additional_drives[index].get("root_percent", 0)
            log_percent = additional_drives[index].get("log_percent", 0)
            if root_percent + log_percent > 100:
                self._raise_error("Invalid input for 'additional_drives' (index %d, drive '%s'): The sum of "
                                  "'root_percent'(%d) and 'log_percent'(%d) must be <= 100 percent" %
                                  (index, additional_drives_sys[index], root_percent, log_percent))
