import base64
import struct
import binascii


def ssh_authorized_keys(self, section):
    for index in range(len(section)):
        self._validate_ssh_key(section[index], index)


def _validate_ssh_key(self, key, index):
    array = key.split()
    # Each rsa-ssh key has 3 different strings in it, first one being
    # type_of_key second one being keystring third one being comment .
    if len(array) < 2:
        self._raise_error("SSH key number %d is not valid.\nSSH Key = %s" % (index, key))
    type_of_key = array[0]
    string = array[1]
    # Must have only valid rsa-ssh key characters ie binascii characters
    try:
        data = base64.b64decode(string)
    except binascii.Error:
        self._raise_error("SSH key number %d is not valid.\nSSH Key = %s" % (index, key))
    int_len = 4
    # Unpack the contents of data, from data[:4], it must be equal to 7, property of ssh key.
    try:
        str_len = struct.unpack('>I', data[:int_len])[0]
    except struct.error:
        self._raise_error("SSH key number %d is not valid.\nSSH Key = %s" % (index, key))
    # data[4:11] must have string which matches with the type_of_key, another ssh key property.
    if not (data[int_len:int_len + str_len].decode("ascii") == type_of_key and int(str_len) == 7):
        self._raise_error("SSH key number %d is not valid.\nSSH Key = %s" % (index, key))
