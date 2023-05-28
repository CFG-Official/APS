import utils.bash_util as BU
from utils.commands_util import commands

@staticmethod
def require_certificate(priv_key_file, out_file, config_file):
    """
        Generates a certificate signing request.
        # Arguments
            priv_key_file: The file containing the private key.
            out_file: The file to output the certificate signing request to.
            config_file: The file containing the configuration for the certificate signing request.
    """
    BU.execute_command(commands["CSR_gen"](priv_key_file, out_file, config_file))
    
@staticmethod
def interactive_require_certificate(fields, priv_key_file, out_file, config_file):
    """ 
        Generates a certificate signing request with the given fields.
        # Arguments
            fields: The fields to use for the certificate signing request.
            priv_key_file: The file containing the private key.
            out_file: The file to output the certificate signing request to.
            config_file: The file containing the configuration for the certificate signing request.
        # Notes
            The number of fields has to be equal to the number of fields in the configuration file.
    """
    inputs = []
    for field in fields:
        inputs.append(input(field))
    BU.execute_command(commands["CSR_interactive_gen"](priv_key_file, out_file, config_file, *inputs))
    
@staticmethod
def view_certificate(in_file):
    """
        Views a certificate signing request.
        # Arguments
            in_file: The file containing the certificate signing request.
        # Returns
            The output of the command.
    """
    return BU.execute_command(commands["CSR_view"](in_file))

@staticmethod
def auto_sign_certificate(days, priv_key_file, out_file, config_file):
    """
        Automatically signs a certificate signing request.
        # Arguments
            days: The number of days the certificate will be valid for.
            priv_key_file: The file containing the private key.
            out_file: The file to output the certificate to.
            config_file: The file containing the configuration for the certificate.
    """
    BU.execute_command(commands["cert_auto_sign"](days, priv_key_file, out_file, config_file))

@staticmethod
def view_auto_certificate(in_file):
    """
        Views an autosigned certificate.
        # Arguments
            in_file: The file containing the certificate.
        # Returns
            The output of the command.
    """
    return BU.execute_command(commands["auto_cert_view"](in_file))