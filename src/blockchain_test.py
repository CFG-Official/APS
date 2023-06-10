from blockchain import Blockchain
from utils.keys_util import gen_ECDSA_keys
from utils.pseudorandom_util import rand_extract
import os


def generate_tuples_list():
    tuples_list = []
    for i in range(5):
        tuples_list.append((rand_extract(16,"hex"),(rand_extract(16,"hex"))))
    return tuples_list


public_key_file = 'server_public_key.pem'
private_key_file = 'server_private_key.pem'
params_file = 'params.txt'
curve_name = 'prime256v1'

os.system(f"rm {public_key_file}")
os.system(f"rm {private_key_file}")
os.system(f"rm {params_file}")


gen_ECDSA_keys(curve_name, params_file,private_key_file,public_key_file)


blockchain = Blockchain(public_key_file, private_key_file)
blockchain.add_block("pre_game", generate_tuples_list())
for i in range(10):
    blockchain.add_block("commit", generate_tuples_list())
    blockchain.add_block("reveal", generate_tuples_list())

os.system(f"rm {public_key_file}")
os.system(f"rm {private_key_file}")
os.system(f"rm {params_file}")