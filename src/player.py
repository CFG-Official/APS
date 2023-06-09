import sys, os, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from user import User
from merkle import merkle_proof
import utils.hash_util as HU
import utils.bash_util as BU
import utils.keys_util as KU
from utils.commands_util import commands
from utils.pseudorandom_util import hash_concat_data_and_known_rand, rand_extract

class Player(User):
    
    """ 
    This class represents a player of the bingo game, it inherits from the User class.
    """

    
    __slots__ = ['game_code', 'player_id', 'security_param']



    def __init__(self, CIE_fields):
        super().__init__(CIE_fields)
        self.game_code = None
        self.player_id = None
        self.security_param = 16 # (in bytes) -> 128 bits
    
    def send_GP(self):
        """ 
        Send the GP certificate to the sala bingo.
        # Returns
            GP_certificate: string
                The name of the GP certificate file.
        """
        return self.GP_certificate
    
    def __compute_proofs(self, policy):
        # value check with merkle proofs
        
        leaves = []
        indices = {}
        index = 0
        for key, value in self.clear_fields.items():
            # append the hashed value of the concatenation between the value and the randomness
            leaves.append(hash_concat_data_and_known_rand(value[0],value[1]))
            indices[key] = index
            index += 1
            
        # verify the merkle proofs for each leaf
        proofs = {}
        for key in policy:
            if key in indices:
                proofs[key] = merkle_proof(leaves, indices[key])
            
        # delete from indices the keys that are not in the policy
        remove = []
        for key in indices.keys():
            if key not in policy:
                remove.append(key)
        
        for key in remove:
            del indices[key]        
        
        return proofs, indices
    
    def send_clear_fields(self, policy):
        """ 
        Send the pairs to the sala bingo.
        # Arguments
            policy: string
                The policy to be used.
        # Returns
            pairs: dictionary
                The dictionary of pairs.
        """
        # return the fields values whose key is in the policy
        proofs, indices = self.__compute_proofs(policy)
        return {key: self.clear_fields[key] for key in policy}, proofs, indices
    
    def start_game(self, game_code, player_id):
        """ 
        Start a game.
        # Arguments
            game_code: string
                The game code.
            player_id: string
                The player id.
        """
        self.game_code = game_code
        self.player_id = player_id

        # Inizializzo la PRF per il calcolo dei contributi casuali
        self.IV = rand_extract(2*self.security_param, "base64")
        self.seed = rand_extract(2*self.security_param, "base64")

    def set_game_code(self, game_code):
        self.game_code = game_code

    def set_player_id(self, player_id):
        self.player_id = player_id

    def generate_message(self):
        # L'output della funzione deve essere (params, comm, signature)
        if self.game_code is None or self.player_id is None:
            raise Exception("Game code or player id not set. This player isn't in a game.")
        
        params = (self.game_code, self.player_id, str(datetime.datetime.now()))
        comm = self.__compute_commitment()
        signature = self.__sign_message(KU.concatenate(*list(params), *comm))

        self.last_message = (params, comm, signature)

        return params, comm, signature

    def __compute_commitment(self):
        # compute the commitment
        # Estraggo dall PRF la concatenazione di contributo casuale e randomness
        prf_output = BU.execute_command(commands["get_prf_value"](self.seed, self.IV)).split('= ')[1].strip()

        # Divide output in two equal parts
        self.last_contribute = prf_output[:len(prf_output)//2]
        self.last_randomess = prf_output[len(prf_output)//2:]

        return HU.compute_hash_from_data(self.last_contribute + self.last_randomess)
    
    def __sign_message(self, message):
        # sign the message
        return KU.sign_ECDSA_from_variable(self.SK, message).split("= ")[1].strip()


