def config_system(self, section):
    install_mgmt_primary = section.get("install_mgmt_primary", False)
    install_mgmt_secondary = section.get("install_mgmt_secondary", False)
    if install_mgmt_primary and install_mgmt_secondary:
        self._raise_error("Only one parameter from ['install_mgmt_primary', 'install_mgmt_secondary'] "
                          "can be set to true.")

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

    gateway_daip = section.get("gateway_daip", False)
    install_security_managment = section.get("install_security_managment", False)
    gateway_cluster_member = section.get("gateway_cluster_member", False)
    if gateway_daip and (install_security_managment or gateway_cluster_member):
        self.rais_error("The parameter 'gateway_daip' must be set to false if one of the parameters "
                        "[install_security_managment, gateway_cluster_member] is set to ture.")
