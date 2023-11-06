def _network_bond(self, interface):
    # Validate each bond slave interface exists and has no ip address
    bond_name = interface["name"]
    bond_interfaces = interface["bond_interfaces"]
    if bond_interfaces is not None:
        for bond_interface in bond_interfaces:
            if bond_interface not in self._seen_interfaces:
                self._raise_error("While configuring slave interfaces for bond %s: %s interface wasn't found"
                                     % (bond_name, bond_interface))
            subnets_addr = self._seen_interfaces[bond_interface]["subnets_addr"]
            if len(subnets_addr) > 0:
                self._raise_error(
                    "While configuring slave interfaces for bond %s: %s interface must not have an ip address"
                    % (bond_name, bond_interface))

    # Validate bond parameters
    if "params" in interface:
        # Check that updelay and downdelay are divided by miimon
        params = interface["params"]
        miimon = params["miimon"] if "miimon" in params else 100
        if "updelay" in params:
            updelay = params["updelay"]
            if updelay % miimon != 0:
                self._raise_error("Updelay parameter must be a multiple of miimon (defualt = 100)")
        if "downdelay" in params:
            downdelay = params["downdelay"]
            if downdelay % miimon != 0:
                self._raise_error("Downdelay parameter must be a multiple of miimon (defualt = 100)")

        mode = params["mode"] if "mode" in params else "round-robin"
        # We can set lacp_rate parameter only if we set the bond mode to '8023AD'
        if "lacp_rate" in params and mode != "8023AD":
            self._raise_error("Configuring of LACP rate can be produced only for 802.3AD mode")

        # We can set xmit_hash_policy parameter only if we set the bond mode to '8023AD' or 'xor'
        if "xmit_hash_policy" in params and mode not in ["8023AD", "xor"]:
            self._raise_error("Transmit Hash Policy can be configured for 802.3AD and balance-xor modes only")
