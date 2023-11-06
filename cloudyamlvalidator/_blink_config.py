def blink_config(self, section):
    install_mds_primary = section.get("install_mds_primary", False)
    install_mds_secondary = section.get("install_mds_secondary", False)
    if install_mds_primary and install_mds_secondary:
        self._raise_error("Only one parameter from ['install_mds_primary', 'install_mds_secondary'] "
                          "can be set to true.")

    install_mds_interface = section.get("install_mds_interface", None)
    if install_mds_interface is not None and install_mds_interface not in self._seen_interfaces:
        self._raise_error("Invalid value for 'install_mds_interface': Interface '%s' does not exist"
                          % install_mds_interface)

    iface = section.get("iface", None)
    if iface is not None and iface not in self._seen_interfaces:
        self._raise_error("Invalid value for 'iface': Interface '%s' does not exist" % iface)
