def _network_vlan(self, interface):
    # Validate pattern of VLAN name and existence of its vlan_link interface
    name = interface["name"]
    vlan_link = interface["vlan_link"]
    vlan_id = interface["vlan_id"]

    lst = name.split(".")
    if vlan_link != lst[0] or vlan_id != int(lst[1]):
        self._raise_error("While configuring VLAN network %s: VLAN's name should be in 'vlan_link.vlan_id' format"
                          % name)

    if vlan_link not in self._seen_interfaces:
        self._raise_error("While configuring VLAN network %s: underlying link interface (%s) must be set first"
                          % (name, vlan_link))

    # VLAN interface's MTU must be smaller or equals to the MTU of its underlying link
    vlan_mtu = interface["mtu"] if "mtu" in interface else 1500
    link_mtu = self._seen_interfaces[vlan_link]["mtu"]
    if vlan_mtu > link_mtu:
        self._raise_error(
            "While configuring VLAN network %s: VLAN's MTU (%d) must not be greater than %s's MTU (%d)"
            % (name, vlan_mtu, vlan_link, link_mtu))
