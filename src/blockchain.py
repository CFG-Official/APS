import os
from blocks import *
import pickle

class Blockchain:
    __blockchain_directory_name = 'Blockchain'
    __blockchain_directory_path = os.path.join(os.getcwd(), __blockchain_directory_name)
    __blockchain_keys_directory_path = os.path.join(__blockchain_directory_path, 'keys')
    __blockchain_signatures_directory_path = os.path.join(__blockchain_directory_path, 'signatures')
    __blockchain_hash_directory_path = os.path.join(__blockchain_directory_path, 'hashes')
    __blockchain_blocks_file = os.path.join(__blockchain_directory_path, 'blocks.txt')

    __slots__ = ['__last_block', '__server_public_key_file', '__server_private_key_file','__actual_public_key_file', '__actual_private_key_file','__block_list']
    def __init__(self, server_public_key_file, server_private_key_file):
        os.system(f"rm -r {self.__blockchain_directory_path}")
        os.system(f"mkdir {self.__blockchain_directory_path}")
        os.system(f"mkdir {self.__blockchain_hash_directory_path}")
        os.system(f"mkdir {self.__blockchain_keys_directory_path}")
        # Copy server keys to blockchain directory
        os.system(f"cp {server_public_key_file} {self.__blockchain_keys_directory_path}/server_public_key.pem")
        os.system(f"cp {server_private_key_file} {self.__blockchain_keys_directory_path}/server_private_key.pem")
        # Set new paths for server keys
        self.__server_public_key_file = os.path.join(self.__blockchain_keys_directory_path, 'server_public_key.pem')
        self.__server_private_key_file = os.path.join(self.__blockchain_keys_directory_path, 'server_private_key.pem')
        self.__actual_public_key_file = self.__server_public_key_file
        self.__actual_private_key_file = self.__server_private_key_file

        os.system(f"mkdir {self.__blockchain_signatures_directory_path}")
        os.system(f"touch {self.__blockchain_blocks_file}")
        self.__block_list = []
        self.__last_block = None

    
    def add_block(self, block_type: str, data: dict):
        block_count = len(self.__block_list)
        print("Last block: ", type(self.__last_block))
        if block_type not in ['pre_game', 'commit', 'reveal', 'end_game']:
            raise TypeError('Invalid block type!')
        
        if block_type == 'pre_game':
            if block_count > 0:
                raise ValueError('Pre-game block must be the first block!')
            
            for user_id, user_pk_temp in data.items():
                data[user_id] = self.__check_entry_pre_game(user_id, user_pk_temp)
            
            self.__last_block = PreGameBlock(self.__blockchain_directory_path, self.__server_public_key_file,self.__server_private_key_file, data)
            
        elif block_type == 'commit':
            if block_count <= 0:
                raise ValueError('Commit block must be at least the second block!')
            
            for user_id, user_commit in data.items():
                self.__check_entry_commit(user_id, user_commit)
            
            self.__last_block = CommitBlock(self.__blockchain_directory_path, block_count, self.__actual_public_key_file, self.__actual_private_key_file,self.__last_block.get_hash() ,data)
        
        elif block_type == 'reveal':
            if block_count <= 1:
                raise ValueError('Reveal block must be at least the third block!')
            
            for user_id, user_reveal in data.items():
                self.__check_entry_reveal(user_id, user_reveal)
            
            self.__last_block = RevealBlock(self.__blockchain_directory_path, block_count, self.__actual_public_key_file, self.__actual_private_key_file,self.__last_block.get_hash() ,data)
        
        
        elif block_type == 'dispute':
            if block_count <= 0:
                raise ValueError('Dispute block must be at least the second block!')
            
            for user_id, user_dispute in data.items():
                self.__check_entry_dispute(user_id, user_dispute)
            
            self.__last_block = DisputeBlock(self.__blockchain_directory_path, block_count, self.__actual_public_key_file, self.__actual_private_key_file,self.__last_block.get_hash() ,data)
        
        
        
        elif block_type == 'end_game':
            if block_count <= 2:
                raise ValueError('End game block must be at least the fourth block!')
            
            for user_id, user_signature in data.items():
                self.__check_entry_end_game(user_id, user_signature)

            self.__last_block = PostGameBlock(self.__blockchain_directory_path, block_count, self.__server_public_key_file, self.__server_private_key_file,self.__last_block.get_hash() ,data)
        
        
        self.append_last_block_to_file()
        
        return self.__last_block
    
    

    def append_last_block_to_file(self):
        Blockchain.append_to_file(self.__blockchain_blocks_file, str(self.__last_block))
        if (len(self.__block_list) == 0) or (self.__block_list[-1] != self.__last_block):
            self.__block_list.append(self.__last_block)


    def set_credentials(self, public_key_file, private_key_file):
        """Set public and private key files for the user who wants to open a dispute."""
        print("Io sono un utente come voi, ma con credenziali diverse!")
        self.__actual_public_key_file = public_key_file
        self.__actual_private_key_file = private_key_file
    

    def reset_server_credentials(self):
        """Reset server credentials to the original ones."""
        self.__actual_public_key_file = self.__server_public_key_file
        self.__actual_private_key_file = self.__server_private_key_file


    @staticmethod
    def append_to_file(file_path, text):
        with open(file_path, 'a') as f:
            f.write(text)

    @final
    @staticmethod
    def __check_user_id(user_id):
        if not isinstance(user_id, str):
            raise TypeError(f'User {user_id} ID is not a string')

    
    @final  
    def __check_entry_pre_game(self,user_id: str, user_pk: str):
        Blockchain.__check_user_id(user_id)
        if not isinstance(user_pk, str):
            raise TypeError(f'User {user_id} has a public key file that is not a string')
        user_pk_file_path = os.path.join(self.__blockchain_keys_directory_path, f'{user_id}_public_key.pem')
        os.system(f"cp {user_pk} {user_pk_file_path}")
        return user_pk_file_path


    @final
    def __check_entry_commit(self, user_id: str, user_commit: tuple):
        Blockchain.__check_user_id(user_id)
        if not isinstance(user_commit, tuple) or len(user_commit) != 3:
            raise TypeError(f'User {user_id} commit is not a Tuple of 3 elements')
        return user_commit
        

    @final
    def __check_entry_reveal(self, user_id: str, user_reveal: tuple):
        Blockchain.__check_user_id(user_id)
        if not isinstance(user_reveal, tuple) or len(user_reveal) != 2:
            raise TypeError(f'User {user_id} reveal is not a Tuple of 2 elements')
        return user_reveal
    
    @final
    def __check_entry_end_game(self, user_id: str, user_signature: str):
        Blockchain.__check_user_id(user_id)
        if not isinstance(user_signature, str):
            raise TypeError(f'User {user_id} signature is not a string')
        return user_signature
    

    @final
    def __check_entry_dispute(self, user_id: str, user_dispute: tuple):
        Blockchain.__check_user_id(user_id)
        if not isinstance(user_dispute, tuple) or (len(user_dispute) != 2 and len(user_dispute) != 3):
            raise TypeError(f'User {user_id} dispute is not a Tuple of 2 or 3 elements!')
        return user_dispute