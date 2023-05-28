import utils.certificates_util as CU
import utils.keys_util as KU
import utils.bash_util as BU
from utils.commands_util import commands

def create_CA(ca_name, priv_key_file, pub_key_file, out_file, curve_name, param_file, days, config_file):
    """ 
    Create a CA with the given name, private key, public key, output file, curve name, parameter file, days and config file.
    # Arguments
        ca_name: string
            The name of the CA.
        priv_key_file: string
            The name of the private key file.
        pub_key_file: string
            The name of the public key file.
        out_file: string
            The name of the output file.
        curve_name: string
            The name of the curve.
        param_file: string
            The name of the parameter file.
        days: int
            The number of days.
        config_file: string
            The name of the config file.
    """
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