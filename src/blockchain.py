import os
import shutil
from pathlib import Path
from blocks import *

class Blockchain:
    __blockchain_directory_name = 'Application/Blockchain'
    __blockchain_directory_path = Path.cwd() / __blockchain_directory_name
    __blockchain_keys_directory_path = __blockchain_directory_path / 'keys'
    __blockchain_signatures_directory_path = __blockchain_directory_path / 'signatures'
    __blockchain_hash_directory_path = __blockchain_directory_path / 'hashes'
    __blockchain_blocks_file = __blockchain_directory_path / 'blocks.txt'

    __slots__ = ['__block_actions','__last_block', '__server_public_key_file', '__server_private_key_file', '__actual_public_key_file', '__actual_private_key_file', '__block_list']
    def __init__(self, server_public_key_file, server_private_key_file):
        
        self.__block_actions = {
            'pre_game': (self.__create_pre_game_block, self.__check_entry_pre_game),
            'commit': (self.__create_commit_block, self.__check_entry_commit),
            'reveal': (self.__create_reveal_block, self.__check_entry_reveal),
            'dispute': (self.__create_dispute_block, self.__check_entry_dispute),
            'end_game': (self.__create_end_game_block, self.__check_entry_end_game),
        }
        
        shutil.rmtree(self.__blockchain_directory_path, ignore_errors=True)
        os.makedirs(self.__blockchain_directory_path, exist_ok=True)
        os.makedirs(self.__blockchain_hash_directory_path, exist_ok=True)
        os.makedirs(self.__blockchain_keys_directory_path, exist_ok=True)
        shutil.copy(server_public_key_file, self.__blockchain_keys_directory_path / 'server_public_key.pem')
        shutil.copy(server_private_key_file, self.__blockchain_keys_directory_path / 'server_private_key.pem')
        self.__server_public_key_file = self.__blockchain_keys_directory_path / 'server_public_key.pem'
        self.__server_private_key_file = self.__blockchain_keys_directory_path / 'server_private_key.pem'
        self.__actual_public_key_file = self.__server_public_key_file
        self.__actual_private_key_file = self.__server_private_key_file
        os.makedirs(self.__blockchain_signatures_directory_path, exist_ok=True)
        self.__blockchain_blocks_file.touch(exist_ok=True)
        self.__block_list = []
        self.__last_block = None

    
    def add_block(self, block_type: str, game_code: str, data: dict, on_chain: bool = False):
        if block_type not in self.__block_actions:
            raise TypeError('Invalid block type!')

        add_func, check_func = self.__block_actions[block_type]

        for user_id, user_data in data.items():
            data[user_id] = check_func(user_id, user_data)

        self.__last_block = add_func(game_code, data, on_chain)
        self.append_last_block_to_file()

        return self.__last_block


    def __create_pre_game_block(self, game_code: str, data: dict, on_chain: bool):
        return PreGameBlock(self.__blockchain_directory_path, self.__server_public_key_file,self.__server_private_key_file, game_code,data)

    def __create_commit_block(self, game_code: str, data: dict, on_chain: bool):
        return CommitBlock(self.__blockchain_directory_path, len(self.__block_list), self.__actual_public_key_file, self.__actual_private_key_file,self.__last_block.get_hash() ,game_code, data, on_chain)

    def __create_reveal_block(self, game_code: str, data: dict, on_chain: bool):
        return RevealBlock(self.__blockchain_directory_path, len(self.__block_list), self.__actual_public_key_file, self.__actual_private_key_file,self.__last_block.get_hash() ,game_code, data, on_chain)

    def __create_dispute_block(self, game_code: str, data: dict, on_chain: bool):
        return DisputeBlock(self.__blockchain_directory_path, len(self.__block_list), self.__actual_public_key_file, self.__actual_private_key_file,self.__last_block.get_hash() ,game_code,data, on_chain)

    def __create_end_game_block(self, game_code: str, data: dict, on_chain: bool):
        return PostGameBlock(self.__blockchain_directory_path, len(self.__block_list), self.__server_public_key_file, self.__server_private_key_file,self.__last_block.get_hash() ,game_code, data)


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
        if len(self.__block_list) > 0:
             raise ValueError('Pre-game block must be the first block!')
        
        Blockchain.__check_user_id(user_id)
        if not isinstance(user_pk, str):
            raise TypeError(f'User {user_id} has a public key file that is not a string')
        user_pk_file_path = os.path.join(self.__blockchain_keys_directory_path, f'{user_id}_public_key.pem')
        os.system(f"cp {user_pk} {user_pk_file_path}")
        return user_pk_file_path


    @final
    def __check_entry_commit(self, user_id: str, user_commit: tuple):
        if len(self.__block_list) <= 0:
            raise ValueError('Commit block must be at least the second block!')
        
        Blockchain.__check_user_id(user_id)
        if not isinstance(user_commit, tuple) or len(user_commit) != 3:
            raise TypeError(f'User {user_id} commit is not a Tuple of 3 elements')
        return user_commit
        

    @final
    def __check_entry_reveal(self, user_id: str, user_reveal: tuple):
        if len(self.__block_list) <= 1:
            raise ValueError('Reveal block must be at least the third block!')
        
        Blockchain.__check_user_id(user_id)
        if not isinstance(user_reveal, tuple) or len(user_reveal) != 2:
            raise TypeError(f'User {user_id} reveal is not a Tuple of 2 elements')
        return user_reveal
    
    @final
    def __check_entry_end_game(self, user_id: str, user_endgame: tuple):
        if len(self.__block_list) <= 2:
            raise ValueError('End game block must be at least the fourth block!')
        
        Blockchain.__check_user_id(user_id)
        if not isinstance(user_endgame, tuple) or len(user_endgame) != 3:
            raise TypeError(f'User {user_id} data is not a Tuple of 3 elements')
        return user_endgame
    

    @final
    def __check_entry_dispute(self, user_id: str, user_dispute: tuple):
        if len(self.__block_list) <= 0:
                raise ValueError('Dispute block must be at least the second block!')
        
        Blockchain.__check_user_id(user_id)
        if not isinstance(user_dispute, tuple) or (len(user_dispute) != 2 and len(user_dispute) != 3):
            raise TypeError(f'User {user_id} dispute is not a Tuple of 2 or 3 elements!')
        return user_dispute