from abc import ABC, abstractmethod
from datetime import datetime
from utils.hash_util import compute_hash_from_data
from utils.pseudorandom_util import rand_extract
from utils.keys_util import sign_ECDSA_from_variable, verify_ECDSA
from utils.keys_util import base64_key_view
import binascii
from typing import final

class AbstractBlock(ABC):
    __slots__ = ['_blockchain_directory_path','_block_number', '_public_key_file' ,'_hash', '_previous_hash', '_timestamp', '_data', '_signature_string', '_signature_file']

    _internal_block_header = "----------START HEADER BLOCK----------\n"
    _internal_block_footer = "----------END HEADER BLOCK----------\n"
    _internal_block_data_header = "----------START DATA BLOCK----------\n"
    _internal_block_data_footer = "\n----------END DATA BLOCK----------\n"

    def __init__(self, blockchain_directory_path:str ,block_number: int, public_key_file: str, private_key_file: str, previous_hash: str, data: dict):
        self._blockchain_directory_path = blockchain_directory_path
        self._block_number = block_number
        self._public_key_file = public_key_file
        self._previous_hash = previous_hash
        self._timestamp = datetime.today()
        self._data = self._check_data(data)
        self._hash = self.__compute_hash()
        self._signature_string = self.__compute_signature(private_key_file)
        

    def get_public_key_file(self):
        return self._public_key_file
    
    def get_signature_string(self):
        return self._signature_string
    
    def get_signature_file(self):
        return self._signature_file

    def get_previous_hash(self):
        return self._previous_hash

    def get_timestamp(self):
        return self._timestamp

    def get_data(self):
        return self._data

    def get_hash(self):
        return self._hash
    
    def verify_block(self, PK):
        """ 
        This method verifies the signature on the current block.
        # Arguments
            PK: the public key of the signer.
        # Returns 
            True if the signature is valid, False otherwise.
        """
        return verify_ECDSA(PK, self.get_data(), self.get_signature_file())

    @abstractmethod
    def __str__(self):
        pass

    
    @abstractmethod
    def _check_data(self, data: dict):
        """ Method to check whether the data for that specific block is well placed.
            Returns the data itself if it is well placed, otherwise throws an exception."""
        pass
    
    @abstractmethod
    def _verify_block(self):
        pass
    
    def _header_string(self):

        public_key = base64_key_view(self._public_key_file)

        output = self._internal_block_header
        output += 'Public Key: ' + public_key + '\n'
        output += f'Timestamp: {self._timestamp}\n'
        output += f'PreviousHash: {self._previous_hash}\n'
        output += self._internal_block_footer
        return output
    
    
    @abstractmethod
    def _data_string(self):
        pass

    
    @final
    def _body_string(self):
        return self._header_string() + self._data_string()
    
    
    @staticmethod
    def binary_to_hex(file_path):
        with open(file_path, 'rb') as f:
            binary_data = f.read()
        return binascii.hexlify(binary_data).decode()

    def __compute_hash(self):
        return compute_hash_from_data(self._body_string())

    def __compute_signature(self, private_key):
        signature_path = f'{self._blockchain_directory_path}/signatures/{self._block_number}.pem'
        sign_ECDSA_from_variable(private_key,self._hash, signature_path)
        self._signature_file = signature_path
        return AbstractBlock.binary_to_hex(signature_path)



class PreGameBlock(AbstractBlock):

    def __init__(self, blockchain_directory_path, public_key_file, private_key_file, data):
        previous_hash = rand_extract(32, 'hex')
        super().__init__(blockchain_directory_path, 0, public_key_file, private_key_file ,previous_hash, data)

    def __str__(self):
        output = '---------------START PRE GAME BLOCK---------------\n'
        output += self._body_string()
        output += f'HashBlock: {self._hash}\n'
        output += f'Signature: {self._signature_string}\n'
        output += '---------------END PRE GAME BLOCK---------------\n\n'
        return output
    
    
    def _check_data(self, data):
        for user_id, user_pk_temp in data.items():
            if not isinstance(user_pk_temp, str):
                raise TypeError(f'User {user_id} public key is not a string')
            if not isinstance(user_id, str):
                raise TypeError(f'User {user_id} ID is not a string')
        return data
    

    def _data_string(self):
        output = self._internal_block_data_header
        for user_id, user_pk_temp in self._data.items():
            output += f'(User: {user_id} - Public Key: {base64_key_view(user_pk_temp)})\n'
        output += self._internal_block_data_footer
        return output
    

    def _verify_block(self):
        pass
    

class CommitBlock(AbstractBlock):

    def __init__(self, blockchain_directory_path, block_number, public_key_file, private_key_file, previous_hash, data):
        super().__init__(blockchain_directory_path, block_number, public_key_file, private_key_file, previous_hash, data)

    def __str__(self):
        output = '\n\n---------------START COMMIT BLOCK---------------\n'
        output += self._body_string()
        output += f'HashBlock: {self._hash}\n'
        output += f'Signature: {self._signature}\n'
        output += '---------------END COMMIT BLOCK---------------\n\n'
        return output
    
    def _check_data(self, data):
        """Commitment,parametro, path_firma"""
        for user_id, user_commit in data.items():
            if not isinstance(user_commit, tuple) or len(user_commit) != 3:
                raise TypeError(f'User {user_id} commit is not a Tuple of 3 elements')            
            if not isinstance(user_id, str):
                raise TypeError(f'User {user_id} ID is not a string')
            return data
    
    def _data_string(self):
        pass
    
    def _verify_block(self):
        pass
    
class RevealBlock(AbstractBlock):

    def __init__(self, blockchain_directory_path, block_number, public_key_file, private_key_file, previous_hash, data):
        super().__init__(blockchain_directory_path, block_number, public_key_file, private_key_file, previous_hash, data)

    def __str__(self):
        output = '\n\n---------------START REVEAL BLOCK---------------\n'
        output += self._body_string()
        output += f'HashBlock: {self._hash}\n'
        output += f'Signature: {self._signature}\n'
        output += '---------------END REVEAL BLOCK---------------\n\n'
        return output
    
    def _check_data(self, data):
        pass
    
    def _data_string(self):
        pass
    
    def _verify_block(self):
        pass
    

class PostGameBlock(AbstractBlock):
    
    def __init__(self, blockchain_directory_path, block_number, public_key_file, private_key_file, previous_hash, data):
        super().__init__(blockchain_directory_path, block_number, public_key_file, private_key_file, previous_hash, data)
    
    def __str__(self):
        output = '\n\n---------------START POST GAME BLOCK---------------\n'
        output += self._body_string()
        output += f'HashBlock: {self._hash}\n'
        output += f'Signature: {self._signature}\n'
        output += '---------------END POST GAME BLOCK---------------'
        return output
    
    def _check_data(self, data):
        pass
    
    def _data_string(self):
        pass
    
    def _verify_block(self):
        pass
    