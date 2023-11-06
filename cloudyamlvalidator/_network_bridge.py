def _network_bridge(self, interface):
    # Validate each bridge slave interface exists and has no ip address
    bridge_name = interface["name"]
    bridge_interfaces = interface["bridge_interfaces"]
    bridge_mtu = interface["mtu"] if "mtu" in interface else 1500
    if bridge_interfaces is not None:
        for bridge_interface in bridge_interfaces:
            if bridge_interface not in self._seen_interfaces:
                self._raise_error("While configuring slave interfaces for bridge %s: %s interface wasn't found"
                                     % (bridge_name, bridge_interface))
            subnets_addr = self._seen_interfaces[bridge_interface]["subnets_addr"]
            if len(subnets_addr) > 0:
                self._raise_error(
                    "While configuring slave interfaces for bridge %s: %s interface must not have an ip address"
                    % (bridge_name, bridge_interface))

            # Bridge's MTU must be smaller or equals to the MTU of its slave interfaces
            mtu = self._seen_interfaces[bridge_interface]["mtu"]
            if mtu < bridge_mtu:
                self._raise_error(
                    "While configuring slave interfaces for bridge %s: Bridge's MTU (%d) must not be greater than"
                    " %s's MTU (%d)" % (bridge_name, bridge_mtu, bridge_interface, mtu))
