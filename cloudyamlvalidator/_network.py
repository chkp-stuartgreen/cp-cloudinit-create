def network(self, section):
    # In case we got an empty list there is nothing to validate
    if section["config"] is None:
        return
    # We run general check only once when _seen_interfaces is still empty
    if not bool(self._seen_interfaces):
        for interface in section["config"]:
            type = interface["type"]
            if type == "physical" or type == "vlan" or type == "bridge" or type == "bond":
                self._network_physical(interface)

    # Special validations according to the interface type
    for interface in section["config"]:
        type = interface["type"]
        if type == "vlan":
            self._network_vlan(interface)
        if type == "bridge":
            self._network_bridge(interface)
        if type == "bond":
            self._network_bond(interface)
        if type == "route":
            self._network_route(interface)
