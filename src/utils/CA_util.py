import utils.certificates_util as CU
import utils.keys_util as KU
import utils.bash_util as BU
from utils.commands_util import commands

def create_CA(ca_name, priv_key_file, pub_key_file, out_file, config_file):
    """ 
    Create a CA with the given name, private key, public key, output file and config file.
    # Arguments
        ca_name: string
            The name of the CA.
        priv_key_file: string
            The name of the private key file.
        pub_key_file: string
            The name of the public key file.
        out_file: string
            The name of the output file.
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
    KU.gen_ECDSA_keys("prime256v1", ca_name+"/param.pem", ca_name+'/'+priv_key_file, ca_name+'/'+pub_key_file)
    # Generate the CA certificate
    CU.auto_sign_certificate(365, ca_name+'/'+priv_key_file, ca_name+'/'+out_file, config_file)
    # Move the CA certificate and key to the CA folder
    # BU.execute_command(commands["move_CA_cert"](ca_name, out_file))
    BU.execute_command(commands["move_CA_key"](ca_name, ca_name+'/'+priv_key_file))
    
def sign_cert(in_file,out_file,config_file):
    """ 
    Sign a certificate with the given input file, output file and config file.
    # Arguments
        in_file: string
            The name of the input file.
        out_file: string
            The name of the output file.
        config_file: string
            The name of the config file.
    """
    BU.execute_command(commands["sign_certificate"](in_file,out_file,config_file))
    
def sign_cert_with_extension(in_file,out_file,config_file,extension_file):
    """ 
    Sign a certificate with the given input file, output file and config file.
    # Arguments
        in_file: string
            The name of the input file.
        out_file: string
            The name of the output file.
        config_file: string
            The name of the config file.
    """
    BU.execute_command(commands["sign_certificate_with_extensions"](in_file,out_file,config_file,extension_file))