import utils.bash_util as BU
from utils.commands_util import commands

def compute_hash_from_data(data):
    """ 
    Compute the hash from the given data.
    # Arguments
        data: string
            The data.
    # Returns
        The hash.
    """
    return BU.execute_command(commands["compute_hash_from_data"](data)).split('= ')[1].strip()

def compute_hash_from_file(in_file, out_file):
    """ 
    Compute the hash from the given file.
    # Arguments
        in_file: string
            The name of the input file.
        out_file: string
            The name of the output file.
        hash_alg: string
            The hash algorithm.
    """
    BU.execute_command(commands["compute_hash_from_file"](in_file, out_file, "-sha3-256"))
    # modify the output file to remove the part before the = sign
    with open(out_file, "r") as f:
        line = f.readline().split('= ')[1].strip()
    with open(out_file, "w") as f:
        f.write(line)
        