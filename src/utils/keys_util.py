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

def sign_ECDSA(priv_key_file, data_file, signature_file):
    """ 
    Sign a file with the given private key.
    # Arguments
        priv_key_file: The file to read the private key from.
        data_file: The file to sign.
        signature_file: The file to store the signature in.
    """
    BU.execute_command(commands["ECDSA_sign"](data_file, priv_key_file, signature_file))

def sign_ECDSA_from_variable(priv_key_file, data_variable, signature_file):
    """ 
    Sign a file with the given private key.
    # Arguments
        priv_key_file: The file to read the private key from.
        data_variable: The variable to sign.
        signature_file: The file to store the signature in.
    """
    return BU.execute_command(commands["ECDSA_sign_variable"](data_variable, priv_key_file, signature_file))

def verify_ECDSA(pub_key_file, data_file, signature_file):
    """
    Verify a file with the given public key.
    # Arguments
        pub_key_file: The file to read the public key from.
        data_file: The file to verify.
        signature_file: The file to read the signature from.
    # Returns
        The output of the command.
    """
    return BU.execute_command(commands["ECDSA_verify"](data_file, signature_file, pub_key_file))

def gen_RSA_keys(key_size, priv_key_file):
    """
    Generates RSA keys using the openssl bash command.
    # Arguments
        key_size: The size of the key to generate.
        priv_key_file: The file to store the private key in.
        pub_key_file: The file to store the public key in.
    """ 
    BU.execute_command(commands["RSA_priv_key_gen"](priv_key_file, key_size))
    
def export_RSA_pub_key(priv_key_file, pub_key_file):
    """
    Exports RSA public key using the openssl bash command.
    # Arguments
        priv_key_file: The file to read the private key from.
        pub_key_file: The file to store the public key in.
    """ 
    BU.execute_command(commands["RSA_pub_key_export"](priv_key_file, pub_key_file))
    
def view_RSA_priv_key(priv_key_file):
    """
    Views RSA private key using the openssl bash command.
    # Arguments
        priv_key_file: The file to read the private key from.
    # Returns
        The output of the command.
    """ 
    return BU.execute_command(commands["RSA_priv_key_view"](priv_key_file))

def view_RSA_pub_key(pub_key_file):
    """
    Views RSA public key using the openssl bash command.
    # Arguments
        pub_key_file: The file to read the public key from.
    # Returns
        The output of the command.
    """ 
    return BU.execute_command(commands["RSA_pub_key_view"](pub_key_file))

def sign_RSA(priv_key_file, data_file, signature_file):
    """
    Signs data using RSA private key using the openssl bash command.
    # Arguments
        priv_key_file: The file to read the private key from.
        data_file: The file to read the data from.
        signature_file: The file to store the signature in.
    """ 
    BU.execute_command(commands["RSA_sign"](data_file, priv_key_file, signature_file))

def verify_RSA(pub_key_file, data_file, signature_file):
    """
    Verifies data using RSA public key using the openssl bash command.
    # Arguments
        pub_key_file: The file to read the public key from.
        data_file: The file to read the data from.
        signature_file: The file to read the signature from.
    """ 
    return BU.execute_command(commands["RSA_verify"](data_file, signature_file, pub_key_file))

def base64_key_view(key_file):
    """
    Views a base64 key using the openssl bash command.
    # Arguments
        key_file: The file to read the key from.
    # Returns
        The output of the command.
    """
    with open(key_file, 'r') as f:
        key = f.read()
    return key.split("-----")[2].replace("\n", "")

def concatenate(*args):
    risultato = ''.join(args)
    return risultato

