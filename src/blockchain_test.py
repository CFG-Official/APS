from blockchain import Blockchain
from utils.keys_util import gen_ECDSA_keys
import os

public_key_file = 'server_public_key.pem'
private_key_file = 'server_private_key.pem'
params_file = 'params.txt'
curve_name = 'prime256v1'

os.system(f"rm {public_key_file}")
os.system(f"rm {private_key_file}")
os.system(f"rm {params_file}")


gen_ECDSA_keys(curve_name, params_file,private_key_file,public_key_file)



blockchain = Blockchain(public_key_file, private_key_file)

os.system(f"rm {public_key_file}")
os.system(f"rm {private_key_file}")
os.system(f"rm {params_file}")