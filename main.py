
import pycdlib
import argparse
import os.path
import sys
import yaml
from cloudyamlvalidator import CloudYamlValidator



# Handle arguments
parser = argparse.ArgumentParser()

parser.add_argument(
    "-u", "--userdata",
    help="path to the cloudinit user_data file",
    default="./user_data.yml"
)
parser.add_argument(
    "-a", "--apiversion",
    help="Openstack dated API version to use for ISO path. EG 2015-10-15.",
    default="2015-10-15"
)
parser.add_argument(
    '-v', '--validate',
    choices=['true', 'false'],
    help='Perform validation of the user data file against the CloudGuard schema',
    default='true'
)
parser.add_argument(
    '-s', '--schema',
    help='Which schema file to validate your user data against. The default will be schema.json in your current directory (included in this package)',
    default=None

)
args = parser.parse_args()

# Validate arguments
#args.userdata = "./sample_config_data.yml"
# userdata file exists
if not os.path.isfile(args.userdata):
    sys.stderr.write("[ERROR] Provided userdata file does not exist")
    exit(1)

# Defaults
userdata_filename = "user_data"
openstack_api_version = args.apiversion
userdata_filepath = f"/openstack/{openstack_api_version}"
override_schema = args.schema if args.schema else "schema.json"

# Validate yaml
if args.validate != 'false':
    try:
        cloud_yaml_validator = CloudYamlValidator(args.userdata, override_schema)
        cloud_yaml_validator.full_validation()
    except yaml.YAMLError as exc:
        sys.stderr.write("Provided YAML file contains one or more errors:\n")
        sys.stderr.write("%s\n" % str(exc).strip())
        exit(1)
else:
    sys.stderr.write("[WARNING] Userdata validation was skipped. ISO will be generated but might not contain valid valid CP cloud-init data.")
iso = pycdlib.PyCdlib()
# Set volume label and ISO type to Joliet
iso.new(joliet=3, vol_ident="config-2")
# Create directories from the root 'up'
iso.add_directory(joliet_path="/openstack")
# Use API version for next level
iso.add_directory(joliet_path=userdata_filepath)
iso.add_file(
    args.userdata, joliet_path=f"{userdata_filepath}/{userdata_filename}")
iso.write('image.iso')
iso.close()
