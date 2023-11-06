from logging import raiseExceptions
import yaml
import subprocess
import re
CHECK_PLATFORM_COMMAND              = "cloud_platform_ex"
METADATA_COMMAND                    = "cloud_metadata"
conditions                          = {}
CLISH_VERSION_COMMAND               = ['cpprod_util', 'CPPROD_GetVerText', 'cpshared']

def default_multi_constructor(loader, tag_suffix, node):
    return ""

def join_string (loader, node):
    join_args = loader.construct_sequence(node, deep=True)
    delimiter = join_args[0]
    joinables = join_args[1]
    return delimiter.join(joinables)


def parse_output(metadata_result):
    output = metadata_result.lower()
    if output == "true" :
        return True
    if output == "false":
        return False
    return metadata_result


def metadata_constructor(loader: yaml.SafeLoader, node: yaml.nodes.ScalarNode) -> str:
    metadata_property = loader.construct_scalar(node)
    if not re.match(r"^([a-zA-Z0-9_])+$", metadata_property):
        exception_string= 'metadata parameter %s is not valid' % metadata_property
        raise Exception(exception_string)
    platform = subprocess.check_output([CHECK_PLATFORM_COMMAND], shell=False)
    platform = (platform.decode("utf-8")).strip()

    command = [METADATA_COMMAND , platform , metadata_property]
    metadata_result = subprocess.check_output(command, shell=False)
    metadata_result = (metadata_result.decode("utf-8")).strip()

    metadata_result  = parse_output(metadata_result)
    return metadata_result


def equal_condition(loader, node):
    join_args = loader.construct_sequence(node, deep=True)
    first_string = join_args[0]
    second_string = join_args[1]
    return first_string == second_string

def and_condition(loader, node):
    and_args = loader.construct_sequence(node, deep=True)
    first_bool = and_args[0]
    second_bool = and_args[1]

    if conditions and first_bool in conditions:
        first_bool = conditions[first_bool]
    elif not type(first_bool) == bool:
        return None

    if conditions and second_bool in conditions:
        second_bool = conditions[second_bool]
    elif not type(second_bool) == bool:
        return None

    return first_bool and second_bool

def or_condition(loader, node):
    and_args = loader.construct_sequence(node, deep=True)
    first_bool = and_args[0]
    second_bool = and_args[1]

    if conditions and first_bool in conditions:
        first_bool = conditions[first_bool]
    elif not type(first_bool) == bool:
        return None

    if conditions and second_bool in conditions:
        second_bool = conditions[second_bool]
    elif not type(second_bool) == bool:
        return None

    return first_bool or second_bool

def not_condition(loader, node):
    args = loader.construct_sequence(node, deep=True)
    condition = args[0]
    if conditions and condition in conditions:
        return True if not conditions[condition] else False
    elif type(condition) == bool:
        return not condition
    else:
        return None


def set_condition(loader, node):
    global conditions
    args = loader.construct_sequence(node, deep=True)
    condition_name = args[0]
    value = args[1]
    if type(value) == bool and condition_name:
        conditions[condition_name] = value
    return {condition_name : value}

def if_condition(loader, node):
    args = loader.construct_sequence(node, deep=True)
    condition = args[0]
    value_true = args[1]
    value_false = args[2]
    if conditions and  condition in conditions and type(conditions[condition]) == bool:
        return value_true if conditions[condition] else value_false
    elif type(condition) == bool:
        return value_true if condition else value_false
    else:
        return None

def gaia_version_constructor(loader: yaml.SafeLoader, node: yaml.nodes.ScalarNode) -> str:
    output = subprocess.check_output(CLISH_VERSION_COMMAND, shell=False)
    output = (output.decode("utf-8")).strip()
    return output

def greater_than_gaia_version(loader, node):
    join_args = loader.construct_sequence(node, deep=True)
    version = join_args[0]
    other_version = join_args[1]
    return float(version[1:]) > float(other_version[1:])

def not_equal_gaia_version(loader, node):
    join_args = loader.construct_sequence(node, deep=True)
    version = join_args[0]
    other_version = join_args[1]
    return float(version[1:]) != float(other_version[1:])

def equal_gaia_version(loader, node):
    join_args = loader.construct_sequence(node, deep=True)
    version = join_args[0]
    other_version = join_args[1]
    return float(version[1:]) == float(other_version[1:])

def less_than_gaia_version(loader, node):
    join_args = loader.construct_sequence(node, deep=True)
    version = join_args[0]
    other_version = join_args[1]
    return float(version[1:]) < float(other_version[1:])

def less_equal_than_gaia_version(loader, node):
    join_args = loader.construct_sequence(node, deep=True)
    version = join_args[0]
    other_version = join_args[1]
    return float(version[1:]) <= float(other_version[1:])

def greater_equal_than_gaia_version(loader, node):
    join_args = loader.construct_sequence(node, deep=True)
    version = join_args[0]
    other_version = join_args[1]
    return float(version[1:]) >= float(other_version[1:])

def get_loader():
    global conditions
    conditions = {}
    loader = yaml.SafeLoader
    loader.add_constructor("!Join", join_string)
    loader.add_constructor("!Metadata", metadata_constructor)
    loader.add_constructor("!Version", gaia_version_constructor)
    loader.add_constructor("!VersionEq", equal_gaia_version)
    loader.add_constructor("!VersionNe", not_equal_gaia_version)
    loader.add_constructor("!VersionLt", less_than_gaia_version)
    loader.add_constructor("!VersionLe", less_equal_than_gaia_version)
    loader.add_constructor("!VersionGt", greater_than_gaia_version)
    loader.add_constructor("!VersionGe", greater_equal_than_gaia_version)
    loader.add_constructor("!Equals", equal_condition)
    loader.add_constructor("!Condition", set_condition)
    loader.add_constructor("!Not", not_condition)
    loader.add_constructor("!And", and_condition)
    loader.add_constructor("!Or", or_condition)
    loader.add_constructor("!If", if_condition)
    return loader