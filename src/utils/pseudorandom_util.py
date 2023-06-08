import base64
import utils.bash_util as BU
import utils.hash_util as HU
from utils.commands_util import commands

def rand_extract(bytes:int, encode:str):
    """
        Generates a pseudo random number.
        # Arguments
            out_file: The file to output the pseudo random number to.
            bytes: The number of bytes to generate.
        # Returns
            The pseudo random number.
        # Raises
            ValueError: If the encoding is invalid.
    """
    enc = "-hex"
    encode = encode.lower()

    if encode== "hex" or encode == "base64":
        enc = "-"+encode
        return (BU.execute_command(commands["rand_extract"](enc,bytes)))
    else:
        raise ValueError("Invalid encoding")
    
def convert_rand_to_num(string:str, encode:str):
    """
        Converts a pseudo random number to a number.
        # Arguments
            string: The string to convert.
            encode: The encoding of the string.
        # Returns
            The converted number.
        # Raises
            ValueError: If the encoding is invalid.
    """
    if encode == "hex":
        return int(string, 16)
    elif encode == "base64":
        return int.from_bytes(base64.b64decode(string), byteorder='big', signed=False)
    else:
        raise ValueError("Invalid encoding")

def pseudo_random_view(in_file,decode:str):
    """
        Views a pseudo random number.
        # Arguments
            in_file: The file to read the pseudo random number from.
    """
    dec = ""
    decode = decode.lower()

    if decode == "bin":
        dec = "b"
    elif decode == "hex":
        dec = "p"
    elif decode == "base64":
        dec = "m"
    
    return BU.execute_command(commands["rand_view"](in_file, dec))


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

def hash_concat_data_and_rand(bytes, data):
    """
        Concatenates the data with a pseudo random number.
        # Arguments
            data: The data to concatenate.
        # Returns
            The concatenated data.
    """
    rand = rand_extract(bytes, "hex")
    return data, rand, HU.compute_hash_from_data((data+rand).removesuffix("\n"))