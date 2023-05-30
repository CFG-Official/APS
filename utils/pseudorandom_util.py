import utils.bash_util as BU
from utils.commands_util import commands

def pseudo_random_gen_bin(out_file, bytes):
    """
        Generates a pseudo random number.
        # Arguments
            out_file: The file to output the pseudo random number to.
            bytes: The number of bytes to generate.
    """
    BU.execute_command(commands["rand_extract_bin"](out_file, bytes))
    
def pseudo_random_gen_hex(out_file, bytes):
    """
        Generates a pseudo random number.
        # Arguments
            out_file: The file to output the pseudo random number to.
            bytes: The number of bytes to generate.
    """
    BU.execute_command(commands["rand_extract_hex"](out_file, bytes))
    
def pseudo_random_gen_base64(out_file, bytes):
    """
        Generates a pseudo random number.
        # Arguments
            out_file: The file to output the pseudo random number to.
            bytes: The number of bytes to generate.
    """
    BU.execute_command(commands["rand_extract_base64"](out_file, bytes))
                       
def pseudo_random_view_bin(in_file):
    """
        Views a pseudo random number.
        # Arguments
            in_file: The file to read the pseudo random number from.
    """
    return BU.execute_command(commands["rand_view_bin"](in_file))

def pseudo_random_view_hex(in_file):
    """
        Views a pseudo random number.
        # Arguments
            in_file: The file to read the pseudo random number from.
    """
    return BU.execute_command(commands["rand_view_hex"](in_file))
    
def pseudo_random_view_base64(in_file):
    """
        Views a pseudo random number.
        # Arguments
            in_file: The file to read the pseudo random number from.
    """
    return BU.execute_command(commands["rand_view_base64"](in_file))