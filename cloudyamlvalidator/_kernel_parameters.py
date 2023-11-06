import re


def kernel_parameters(self, section):
    # We do not validate kernel_Parameters during internal robot test since we are not in GAIA OS.
    if self._internal_test:
        return
    if "sim" in section and section["sim"] is not None:
        self._validate_parameters(section["sim"], "simkern")
    if "fw" in section and section["fw"] is not None:
        self._validate_parameters(section["fw"], "fwkern")


def _validate_parameters(self, section, target):
    supported_param_type = ['string', 'int', 'uint', 'long', 'ulong', 'array of int', 'array of charp']
    param_to_type = self._create_dictionary(target)
    error_msg = ""

    for param_and_value in section:
        param = param_and_value.split("=")[0].strip()
        value = param_and_value.split("=")[1].strip()

        if param in param_to_type:
            param_type = param_to_type[param]
        else:
            self._raise_error("The parameter '%s' doesn't supported for %s." % (param, target))

        if param_type not in supported_param_type:
            self._raise_error("The %s parameter '%s' has unsupported datatype (%s)." % (target, param, param_type))
        elif param_type == 'string':
            continue
        elif param_type in ['int', 'uint', 'long', 'ulong']:
            try:
                value = int(value)
                if param_type == 'int' and self._check_if_int(value, unsigned=False):
                    continue
                elif param_type == 'uint' and self._check_if_int(value, unsigned=True):
                    continue
                elif param_type == 'long' and self._check_if_long(value, unsigned=False):
                    continue
                elif param_type == 'ulong' and self._check_if_long(value, unsinged=True):
                    continue
            except ValueError:
                pass

        # param_type in ['array of int', 'array of charp']
        else:
            lst = value.split(",")
            if len(lst) == 0:
                error_msg = "Got empty list"

            else:
                valid = True
                if param_type == 'array of int':
                    try:
                        for val in lst:
                            val = int(val)
                            if self._check_if_int(val, unsigned=False):
                                error_msg = "The value %s is not in type 'int'." % (str(val))
                                valid = False
                                break

                    except ValueError:
                        error_msg = "The value %s is not in type 'int'." % (str(val))
                        valid = False

                if valid:
                    continue

        # Got in valid value according to the parameter type
        self._raise_error("Got invalid kernel parameter: %s must be in type '%s'. %s" % (param, param_type, error_msg))


def _create_dictionary(self, target):
    FW_KERN_PATH = "$FWDIR/boot/modules/fw_kern_"
    SIM_KERN_PATH = "$PPKDIR/boot/modules/sim_kern_"
    TMP_PARAMS_FILE = "/opt/CPcge/bin/params"
    if target == 'fwkern':
        path = FW_KERN_PATH
    elif target == 'simkern':
        path = SIM_KERN_PATH
    else:
        self._raise_error("Target must be fwkern or simkern. (got %s)" % target)
    path += '64_3_10_64.o' if self._ipv4_mod else '64_3_10_64_v6.o'

    param_to_type = {}
    re_format = "^parm:[\t ]*([a-z_]{1,}):.*\(([a-z ]*)\)$"

    # Better memory performance if we read line by line instead the whole file at once
    self._run_shell("modinfo %s > %s" % (path, TMP_PARAMS_FILE))

    with open(TMP_PARAMS_FILE) as fd:
        line = fd.readline()
        while line:
            match = re.match(re_format, line)
            if match:
                param_to_type[match.group(1)] = match.group(2).strip()
            line = fd.readline()

    self._run_shell("rm %s" % TMP_PARAMS_FILE)
    return param_to_type


def _check_if_int(self, val, unsigned=False):
    UINT_MAX_VALUE = 2 ** 32
    if unsigned:
        return 0 <= val <= UINT_MAX_VALUE - 1
    else:
        return -UINT_MAX_VALUE / 2 <= val <= UINT_MAX_VALUE / 2 - 1


def _check_if_long(self, val, unsigned=False):
    ULOG_MAX_VALUE = 2 ** 64
    if unsigned:
        return 0 <= val <= ULOG_MAX_VALUE - 1
    else:
        return -ULOG_MAX_VALUE / 2 <= val <= ULOG_MAX_VALUE / 2 - 1
