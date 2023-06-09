from abc import ABC, abstractmethod
from datetime import datetime
from utils.hash_util import compute_hash_from_data
from utils.pseudorandom_util import rand_extract
from utils.keys_util import sign_ECDSA_from_variable
from utils.keys_util import base64_key_view
import binascii

class AbstractBlock(ABC):
    __slots__ = ['_blockchain_directory_path','_block_number', '_public_key' ,'_hash', '_previous_hash', '_timestamp', '_data', '_signature']

    def __init__(self, blockchain_directory_path:str ,block_number: int, public_key: str, private_key: str, previous_hash: str, data: list):
        self._blockchain_directory_path = blockchain_directory_path
        self._block_number = block_number
        self._public_key = public_key
        self._previous_hash = previous_hash
        self._timestamp = datetime.today()
        self._data = data
        self._hash = self.__compute_hash()
        self._signature = self.__compute_signature(private_key)
        

    @property
    def public_key(self):
        return self._public_key

    @property
    def previous_hash(self):
        return self._previous_hash

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def data(self):
        return self._data

    @abstractmethod
    def __str__(self):
        pass

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
        return AbstractBlock.binary_to_hex(signature_path)


    def _body_string(self):

        public_key = base64_key_view(self._public_key)

        output = '------ START HEADER BLOCK ------\n'
        output += 'Public Key: ' + public_key + '\n'
        output += f'Timestamp: {self._timestamp}\n'
        output += f'PreviousHash: {self._previous_hash}\n'
        output += '------ END HEADER BLOCK ------\n'
        output += '------ START DATA BLOCK ------\n'
        for item in self._data:
            output += str(item) + '\n'
        output += '------ END DATA BLOCK ------\n'
        return output


class PreGameBlock(AbstractBlock):

    def __init__(self, blockchain_directory_path, public_key, private_key, data):
        previous_hash = rand_extract(32, 'hex')
        super().__init__(blockchain_directory_path, 0, public_key, private_key ,previous_hash, data)

    def __str__(self):
        output = '--- START PRE GAME BLOCK ---\n'
        output += self._body_string()
        output += f'HashBlock: {self._hash}\n'
        output += f'Signature: {self._signature}\n'
        output += '--- END PRE GAME BLOCK ---\n'
        return output