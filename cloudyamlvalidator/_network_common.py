def _get_ip_and_mask_ipv4(self, ip_and_mask: str, netmask: str):
    if netmask:
        ip = ip_and_mask
        mask_bits = self._convert_mask_to_prefix_ipv4(netmask)
    else:
        ip_and_mask = ip_and_mask.split('/')
        ip = ip_and_mask[0]
        mask_bits = ip_and_mask[1]

    return ip, mask_bits


def _check_subnets_intersect_cidr_ipv4(self, net_addr1: str, net_addr2: str):
    address1 = net_addr1.split('/')[0]
    address2 = net_addr2.split('/')[0]
    mask1 = int(net_addr1.split('/')[1])
    mask2 = int(net_addr2.split('/')[1])

    mask = mask1 if mask1 < mask2 else mask2
    address1 = self._get_subnet_address_ipv4(address1, str(mask)).split('/')[0]
    address2 = self._get_subnet_address_ipv4(address2, str(mask)).split('/')[0]

    # The two subnets intersect iff address1 == address2
    return address1 == address2


def _get_subnet_address_ipv4(self, ip: str, mask_bits: str):
    res = ""
    mask = int(mask_bits)
    ip_lst = list(map(int, ip.split('.')))
    for i in range(4):
        num = ip_lst[i]
        new_num = 0
        for j in range(7, -1, -1):
            mask -= 1
            coefficient = 1 if mask >= 0 else 0
            new_num |= (coefficient * 2**j & num)

        res += str(new_num) + '.'

    return res[:-1] + "/" + mask_bits


def _convert_mask_to_prefix_ipv4(self, mask: str):
    res = 0
    lst = list(map(int, mask.split('.')))
    for i in range(len(lst)):
        if lst[i] == 255:
            res += 8
        else:
            power = 8
            tmp = 0
            while tmp < lst[i]:
                res += 1
                power -= 1
                tmp += 2 ** power
            break

    return str(res)
