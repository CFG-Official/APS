import utils.certificates_util as CU
import utils.keys_util as KU
import utils.bash_util as BU
from utils.commands_util import commands

def create_CA(ca_name, priv_key_file, pub_key_file, out_file, curve_name, param_file, days, config_file):
    # Create the CA folder
    BU.execute_command(commands["create_CA_main_dir"](ca_name))
    BU.execute_command(commands["create_CA_key_dir"](ca_name))
    BU.execute_command(commands["create_CA_cert_dir"](ca_name))
    BU.execute_command(commands["create_CA_index_file"](ca_name))
    BU.execute_command(commands["create_CA_serial_file"](ca_name))
    # Generate the CA key
    KU.gen_ECDSA_keys(curve_name, param_file, priv_key_file, pub_key_file)
    # Generate the CA certificate
    CU.auto_sign_certificate(days, priv_key_file, out_file, config_file)
    # Move the CA certificate and key to the CA folder
    BU.execute_command(commands["move_CA_cert"](ca_name, out_file))
    BU.execute_command(commands["move_CA_key"](ca_name, priv_key_file))