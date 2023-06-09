from abc import ABC, abstractmethod
from datetime import datetime
from utils.hash_util import compute_hash_from_data

class AbstractBlock(ABC):
    __slots__ = ['_public_key', '_hash', '_previous_hash', '_timestamp', '_data', '_signature']

    def __init__(self, public_key, previous_hash, private_key):
        self._public_key = public_key
        self._previous_hash = previous_hash
        self._timestamp = datetime.today()
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

    @abstractmethod
    def __compute_hash(self):
        return compute_hash_from_data(self.__body_string())

    @abstractmethod
    def __compute_signature(self, private_key):
        pass

    def __body_string(self):
        output += '------ START HEADER BLOCK ------\n'
        output += f'Public Key: {self._public_key}\n'
        output += f'Timestamp: {self._timestamp}\n'
        output += f'PreviousHash: {self._previous_hash}\n'
        output += '------ END HEADER BLOCK ------\n'
        output += '------ START DATA BLOCK ------\n'
        for item in self._data:
            output += str(item) + '\n'
        output += '------ END DATA BLOCK ------\n'
        return output


class PreGameBlock(AbstractBlock):

    def __init__(self, public_key, previous_hash, private_key, data):
        self._data = data
        super().__init__(public_key, previous_hash, private_key)

    def __str__(self):
        output = '--- START PRE GAME BLOCK ---\n'
        output += '------ START HEADER BLOCK ------\n'
        output += f'Public Key: {self._public_key}\n'
        output += f'Timestamp: {self._timestamp}\n'
        output += f'PreviousHash: {self._previous_hash}\n'
        output += '------ END HEADER BLOCK ------\n'
        output += '------ START DATA BLOCK ------\n'
        for item in self._data:
            output += str(item) + '\n'
        output += '------ END DATA BLOCK ------\n'
        output += f'HashBlock: "{self._hash}"\n'
        output += f'Signature: "{self._signature}"\n'
        output += '--- END PRE GAME BLOCK ---\n'
        return output

    def __compute_hash(self):
        pass

    def __compute_signature(self, private_key):
        pass
