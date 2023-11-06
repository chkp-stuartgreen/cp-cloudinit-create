def _network_physical(self, interface):
    name = interface["name"]
    if name in self._seen_interfaces.keys():
        self._raise_error("There is already a network interface with the name %s" % name)

    mtu = interface["mtu"] if "mtu" in interface else 1500
    mac_addr = interface["mac_address"] if "mac_address" in interface else None
    subnets_addr = []

    if mac_addr is not None:
        self._validate_mac_address(mac_addr, name)

    if "subnets" in interface and interface["subnets"] is not None:
        for subnet in interface["subnets"]:
            # Subnet address validation
            subnets_addr.append(self._validate_subnet_address(subnet, name))

            # Subnet routes validation
            if "routes" in subnet and subnet["routes"] is not None:
                for route in subnet["routes"]:
                    self._validate_route(route, name)

    self._seen_interfaces[name] = {"mtu": mtu, "mac_addr": mac_addr, "subnets_addr": subnets_addr}


def _validate_subnet_address(self, subnet, interface_name):
    # We support dotted format or CIDR notation but not both
    ip_and_mask = subnet.get("address")
    netmask = subnet.get("netmask", None)
    if not (netmask is not None) ^ ('/' in ip_and_mask):
        self._raise_error(
            "Network interface %s contains invalid netmask setting for address %s:\n"
            "Expected netmask in dotted format OR ip address with CIDR notation"
            % (interface_name, ip_and_mask.split('/')[0]))

    # Verifying we do not have two conflicting subnets
    (ip, mask_bits) = self._get_ip_and_mask_ipv4(ip_and_mask, netmask)
    this_subnet_address = self._get_subnet_address_ipv4(ip, mask_bits)
    for properties_dict in self._seen_interfaces.values():
        for subnet_address in properties_dict["subnets_addr"]:
            if self._check_subnets_intersect_cidr_ipv4(this_subnet_address, subnet_address):
                self._raise_error(
                    "Network interface %s contains subnet address that "
                    "conflicts with another subnet" % interface_name)

    return this_subnet_address


def _validate_route(self, route, interface_name):
    # We support dotted format or CIDR notation but not both
    ip_and_mask = route.get("destination")
    netmask = route.get("netmask", None)
    if not (netmask is not None) ^ ('/' in ip_and_mask):
        self._raise_error(
            "Network interface %s contains invalid netmask setting for route destination %s:\n"
            "Expecting for netmask in dotted format OR ip address with CIDR notation"
            % (interface_name, ip_and_mask.split('/')[0]))

    (ip, mask_bits) = self._get_ip_and_mask_ipv4(ip_and_mask, netmask)
    dest_network_address = self._get_subnet_address_ipv4(ip, mask_bits).split("/")[0]
    if ip != dest_network_address:
        self._raise_error(
            "Network interface %s contains route destination address that is "
            "not a subnet address: Got %s, Expecting for %s." % (interface_name, ip, dest_network_address))


def _validate_mac_address(self, mac_address, interface_name):
    for interface in self._seen_interfaces.keys():
        if self._seen_interfaces[interface]["mac_addr"] == mac_address:
            self._raise_error(
                "Network interface %s has MAC address that is already used by another interface (%s)\n"
                % (interface_name, interface)
            )
