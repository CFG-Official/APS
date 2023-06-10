import os
from blocks import *
class Blockchain:
    __blockchain_directory_name = 'Blockchain'
    __blockchain_directory_path = os.path.join(os.getcwd(), __blockchain_directory_name)
    __blockchain_keys_directory_path = os.path.join(__blockchain_directory_path, 'keys')
    __blockchain_signatures_directory_path = os.path.join(__blockchain_directory_path, 'signatures')
    __blockchain_block_directory_path = os.path.join(__blockchain_directory_path, 'blocks')
    __blockchain_blocks_file = os.path.join(__blockchain_directory_path, 'blocks.txt')

    __slots__ = ['__blockcount', '__last_block', '__server_public_key_file', '__server_private_key_file']

    def __init__(self, server_public_key_file, server_private_key_file):
        os.system(f"rm -r {self.__blockchain_directory_path}")
        os.system(f"mkdir {self.__blockchain_directory_path}")
        os.system(f"mkdir {self.__blockchain_keys_directory_path}")
        
        # Copy server keys to blockchain directory
        os.system(f"cp {server_public_key_file} {self.__blockchain_keys_directory_path}/server_public_key.pem")
        os.system(f"cp {server_private_key_file} {self.__blockchain_keys_directory_path}/server_private_key.pem")
        # Set new paths for server keys
        self.__server_public_key_file = os.path.join(self.__blockchain_keys_directory_path, 'server_public_key.pem')
        self.__server_private_key_file = os.path.join(self.__blockchain_keys_directory_path, 'server_private_key.pem')
        os.system(f"mkdir {self.__blockchain_signatures_directory_path}")
        os.system(f"mkdir {self.__blockchain_block_directory_path}")
        os.system(f"touch {self.__blockchain_blocks_file}")
        self.__blockcount = 0
        self.add_block('pre_game', [("PlayerID","Player_PK")])

    
    def add_block(self, block_type: str, data: list):
        if block_type not in ['pre_game', 'commit', 'reveal']:
            raise TypeError('Invalid block type!')
        
        if block_type == 'pre_game':
            if self.__blockcount > 0:
                raise ValueError('Pre-game block must be the first block!')
            self.__last_block = PreGameBlock(self.__blockchain_directory_path, self.__server_public_key_file,self.__server_private_key_file, data)
            
        elif block_type == 'commit':
            if self.__blockcount <= 0:
                raise ValueError('Commit block must be at least the second block!')
        elif block_type == 'reveal':
            if self.__blockcount <= 1:
                raise ValueError('Reveal block must be at least the third block!')
        
        self.__blockcount += 1
        self.append_last_block_to_file()
    
    

    def append_last_block_to_file(self):
        Blockchain.append_to_file(self.__blockchain_blocks_file, str(self.__last_block))
    
    @staticmethod
    def append_to_file(file_path, text):
        with open(file_path, 'a') as f:
            f.write(text)


