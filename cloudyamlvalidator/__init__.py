import subprocess
import inspect
import yaml
from pathlib import Path
import jsonschema
import custom_tags_loader


class CloudYamlValidator(object):
    def __init__(self, filename, schema_path=None, internal_test=None):
        self._seen_interfaces = {}
        self._ipv4_mod = True
        self._filename = filename
        self._config = {}
        self._SCHEMA = schema_path if schema_path else "/opt/CPcge/bin/schema.json"
        self._internal_test = internal_test == 'true'

    from cloudyamlvalidator._network import network
    from cloudyamlvalidator._network_physical import _network_physical, _validate_subnet_address, _validate_route, _validate_mac_address
    from cloudyamlvalidator._network_vlan import _network_vlan
    from cloudyamlvalidator._network_bond import _network_bond
    from cloudyamlvalidator._network_bridge import _network_bridge
    from cloudyamlvalidator._network_route import _network_route
    from cloudyamlvalidator._network_common import _get_ip_and_mask_ipv4, _check_subnets_intersect_cidr_ipv4, _get_subnet_address_ipv4, _convert_mask_to_prefix_ipv4
    from cloudyamlvalidator._ssh_authorized_keys import ssh_authorized_keys, _validate_ssh_key
    from cloudyamlvalidator._kernel_parameters import kernel_parameters, _validate_parameters, _create_dictionary, _check_if_int, _check_if_long
    from cloudyamlvalidator._write_files import write_files, _validate_encoding, _is_base64, _is_gzip
    from cloudyamlvalidator._blink_config import blink_config
    from cloudyamlvalidator._config_system import config_system
    from cloudyamlvalidator._growpart import growpart

    def full_validation(self):
        # load YAML from filename
        self.basic_validation()
        # Validate the user YAML against JSON schema
        self._compare_to_schema()
        # We want to validate network section (if exists) first in order to initiate seen_interfaces
        # dictionary, which may be used during validation of other sections
        if "network" in self._config and self._config["network"] is not None:
            self.network(self._config["network"])
        # Validate each section according to the appropriate function
        for section in self._config:
            if section == "network" or self._config[section] is None:
                continue
            func_name = section
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                if callable(func):
                    func(self._config[section])

    def basic_validation(self, aliases_files=[]):
        try:
            # First try loading user YAML filename file
            try:
                filename_txt = Path(self._filename).read_text()
                self._config = yaml.load(filename_txt, Loader=custom_tags_loader.get_loader())

            # If failed, try to load it with the rest of aliases_file
            except yaml.composer.ComposerError as exc:
                if "alias" in exc.problem:
                    aliases_files_txt = ""
                    for alias_file in aliases_files:
                        aliases_files_txt += Path(alias_file).read_text()
                    merged_txt = aliases_files_txt + filename_txt
                    self._config = yaml.load(merged_txt, Loader=custom_tags_loader.get_loader())

        except FileNotFoundError as exc:
            self._raise_error("File %s was not found" % exc.filename)
        except yaml.composer.ComposerError as exc:
            if "alias" in exc.problem:
                self._raise_error("YAML file %s contains undefined aliases: %s" % (self._filename, exc.problem))
        except yaml.parser.ParserError as exc:
            self._raise_error("YAML file %s is not valid: %s" % (self._filename, exc.problem))

    def _compare_to_schema(self):
        # Validate the user YAML against JSON schema
        schema_txt = Path(self._SCHEMA).read_text()
        jsonSchema = yaml.load(schema_txt, Loader=custom_tags_loader.get_loader())
        validator = jsonschema.Draft4Validator(jsonSchema)
        errors = [error.message for error in validator.iter_errors(self._config)]

        if any(True for _ in errors):
            errors_msg = ""
            error_num = 1
            for error in errors:
                errors_msg += "%d: %s\n" % (error_num, error)
                error_num += 1
            self._raise_error("YAML is not compatible with provided JSON schema:\n%s" % errors_msg)

    def _run_shell(self, command):
        try:
            output = subprocess.check_output(command, shell=True).decode('ascii')
        except subprocess.SubprocessError:
            output = ""
        return output.strip()

    def _raise_error(self, message):
        caller_function_name = inspect.stack()[1].function
        raise yaml.YAMLError("Error in function %s:\n%s" % (caller_function_name, message))
