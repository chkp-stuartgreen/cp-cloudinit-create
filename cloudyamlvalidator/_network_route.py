def _network_route(self, interface):
    # We support dotted format or CIDR notation but not both
    ip_and_mask = interface.get("destination")
    netmask = interface.get("netmask", None)
    if not (netmask is not None) ^ ('/' in ip_and_mask):
        self._raise_error(
            "Network section contains route with invalid netmask setting for destination %s:\n"
            "Expecting for netmask in dotted format OR ip address with CIDR notation"
            % (ip_and_mask.split('/')[0]))

    (ip, mask_bits) = self._get_ip_and_mask_ipv4(ip_and_mask, netmask)
    dest_network_address = self._get_subnet_address_ipv4(ip, mask_bits).split("/")[0]
    if ip != dest_network_address:
        self._raise_error(
            "Network section contains route with destination address that is "
            "not a subnet address: Got %s, Expecting for %s." % (ip, dest_network_address))
