import utils.bash_util as BU
from utils.commands_util import commands

def gen_ECDSA_keys(curve_name, param_file, priv_key_file, pub_key_file):
    """
    Generates ECDSA keys using the openssl bash command.
    # Arguments
        curve_name: The name of the curve to use.
        param_file: The file to store the parameters in.
        priv_key_file: The file to store the private key in.
        pub_key_file: The file to store the public key in.
    """ 
    BU.execute_command(commands["ECDSA_params_gen"](curve_name, param_file))
    BU.execute_command(commands["ECDSA_priv_key_gen"](param_file, priv_key_file))
    BU.execute_command(commands["ECDSA_pub_key_gen"](priv_key_file, pub_key_file))
    
def view_ECDSA_params(param_file):
    """
    Views ECDSA parameters using the openssl bash command.
    # Arguments
        param_file: The file to read the parameters from.
    # Returns
        The output of the command.
    """ 
    return BU.execute_command(commands["ECDSA_params_view"](param_file))
    
def view_ECDSA_priv_key(priv_key_file):
    """
    Views ECDSA private key using the openssl bash command.
    # Arguments
        priv_key_file: The file to read the private key from.
    # Returns
        The output of the command.
    """ 
    return BU.execute_command(commands["ECDSA_priv_key_view"](priv_key_file))
    
def view_ECDSA_pub_key(pub_key_file):
    """
    Views ECDSA public key using the openssl bash command.
    # Arguments
        pub_key_file: The file to read the public key from.
    # Returns
        The output of the command.
    """ 
    return BU.execute_command(commands["ECDSA_pub_key_view"](pub_key_file))

