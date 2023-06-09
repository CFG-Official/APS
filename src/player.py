import sys, os, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from user import User
from merkle import merkle_proof
from utils.hash_util import compute_hash_from_data
from utils.bash_util import execute_command
from utils.keys_util import concatenate, sign_ECDSA, verify_ECDSA
from utils.commands_util import commands
from utils.pseudorandom_util import hash_concat_data_and_known_rand, rand_extract
from utils.hash_util import compute_hash_from_data

class Player(User):
    
    """ 
    This class represents a player of the bingo game, it inherits from the User class.
    """
        
    __slots__ = ['game_code', 'player_id', 'security_param', '_final_string', '_contr_comm', '_contr_open']

    def __init__(self, CIE_fields):
        super().__init__(CIE_fields)
        self.game_code = None
        self.player_id = None
        self.security_param = 16 # (in bytes) -> 128 bits
        self._contr_comm = []
        self._contr_open = []
        self._final_string = None
    
    # AUTHENTICATION

    def send_GP(self):
        """ 
        Send the GP certificate to the sala bingo.
        # Returns
            GP_certificate: string
                The name of the GP certificate file.
        """
        return self.GP_certificate

    def set_PK_bingo(self, bingo_PK):
        """ 
        Set the PK of the sala bingo.
        # Arguments
            bingo_PK: string
                The name of the sala bingo public key file.
        """
        self._bingo_PK = bingo_PK
    
    def __compute_proofs(self, policy):
        """
        Given a policy, compute the merkle proofs for the leaves that are in the policy
        # Arguments
            policy: string
                The policy to access bingo

        # Returns
            proofs: dictionary
                A dictionary containing the merkle proofs for the leaves that are in the policy.
                Key are the name of the field (opening of leaf) and values are the merkle proofs.
        """
        
        leaves = []
        indices = {} # map the properties (key) to the index of leaves list (value)
        index = 0 

        # Compute the commitment (aka the leaves of the merkle tree) for each field in the policy
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
    
    # GAME    

    def start_game(self, game_code, player_id):
        """ 
        Start a game.
        # Arguments
            game_code: string
                The game code.
            player_id: string
                The player id.
        """
        self.set_game_code(game_code)
        self.set_player_id(player_id)

        # Inizializzo la PRF per il calcolo dei contributi casuali
        self.IV = rand_extract(2*self.security_param, "base64")
        self.seed = rand_extract(2*self.security_param, "base64")

    def set_game_code(self, game_code):
        self.game_code = game_code

    def set_player_id(self, player_id):
        self.player_id = player_id

    def __generate_message(self):
        # L'output della funzione deve essere (params, comm, signature)
        if self.game_code is None or self.player_id is None:
            raise Exception("Game code or player id not set. This player isn't in a game.")
        
        params = (self.game_code, self.player_id, str(datetime.datetime.now()))
        comm = self.__compute_commitment()
        signature = self.__sign_message(concatenate(*list(params), *comm))

        self.last_message = (params, comm, signature)

        return params, comm, signature

    def __compute_commitment(self):
        # compute the commitment
        # Estraggo dall PRF la concatenazione di contributo casuale e randomness
        prf_output = execute_command(commands["get_prf_value"](self.seed, self.IV)).split('= ')[1].strip()

        # Divide output in two equal parts
        self.last_contribute = prf_output[:len(prf_output)//2]
        self.last_randomess = prf_output[len(prf_output)//2:]

        return compute_hash_from_data(self.last_contribute + self.last_randomess)
    
    def __sign_message(self, message):
        with open(self.user_name+'/'+self.user_name+"_temp.txt", "w") as f:
            f.write(message)
        # sign the message
        sign_ECDSA(self.SK, self.user_name+'/'+self.user_name+"_temp.txt", self.user_name+'/'+self.user_name+'_comm_sign.pem')
        return self.user_name+'/'+self.user_name+'_comm_sign.pem'
        #return sign_ECDSA_from_variable(self.SK, message).split("= ")[1].strip()
    
    def send_commitment(self): # Nome da cambiare, non è solo il commitment
        """
        The player computes its own commitment, and computes the signature
        on the committment. Then he sends them and the game parameters
        (timestamp, player_id and game_id).
        # Returns
            params: tuple
                The game parameters.
            commitment: string
                The commitment.
            signature: string
                The signature of the player on the commitment.
        """
        return self.__generate_message()
    
    def receive_signature(self, signature):
        """ 
        The player receives the signature of the sala bingo on the commitment,
        the signature and the additional parameters. Then it verifies the 
        signature.
        # Returns
            true if the signature is valid, false otherwise.
        """
        # verify the signature of the sala bingo on the concatenation of the additional 
        # parameters, the commitment and the signature
        concat = ""
        for param in self.last_message[0]:
            concat += param
        concat += self.last_message[1]
        concat += self.last_message[2]
        with open(self.user_name+'/'+self.user_name+"_temp.txt", "w") as f: 
            f.write(concat)
        if verify_ECDSA(self._bingo_PK, self.user_name+'/'+self.user_name+"_temp.txt", signature):
            self._bingo_sign_on_comm = signature
            return True
        return False
    
    def receive_commitments_and_signature(self, pairs, signature):
        """
        The player receives the commitments, the parameters and the 
        signature of the sala bingo on them. Then it verifies the 
        signature.
        
        # Arguments
            pairs: list
                The list of pairs.
            signature: string
                The signature of the sala bingo on the list of pairs concatenated.
                
        # Returns
            true if the signature is valid, false otherwise.
        """
        self._contr_comm = pairs
        concat = ""
        for pair in pairs:
            for param in pair[0]:
                concat += param
            concat += pair[1]
        with open(self.user_name+'/'+self.user_name+"_temp.txt", "w") as f:
            f.write(concat)
        if verify_ECDSA(self._bingo_PK, self.user_name+'/'+self.user_name+"_temp.txt", signature):
            self._bingo_sign_on_comm = signature
            return True
        return False
    
    def send_opening(self):
        """ 
        The player sends its opening to the sala bingo.
        # Returns
            opening: string
                The opening as (message, randomness) pair.
        """
        return self.last_contribute, self.last_randomess

    def __compute_final_string(self):
        # hash the concatenation of all the openings
        concat = ""
        for opening in self._contr_open:
            concat += opening[0]
        return compute_hash_from_data(concat)
    
    def __verify_commitments(self):
        for contr, opening in zip(self._contr_comm, self._contr_open):
            if contr[1] != hash_concat_data_and_known_rand(opening[0], opening[1]):
                return False
        return True
    
    def receive_openings(self, openings, signature):
        """ 
        The player receives the openings from the sala bingo and computes
        the final string.
        # Arguments
            openings: list
                The list of openings (message, randomness).
        """
        self._contr_open = openings
        
        if self.__verify_commitments():
            concat = ""
            for contr, opening in zip(self._contr_comm, self._contr_open):
                for param in contr[0]:
                    concat += param
                concat += contr[1] + opening[0] + opening[1]
            with open(self.user_name+'/'+self.user_name+"_temp.txt", "w") as f:
                f.write(concat)
            res = verify_ECDSA(self._bingo_PK, self.user_name+'/'+self.user_name+"_temp.txt", signature)
            self._final_string = self.__compute_final_string()
            return res
        else:
            raise Exception("Commitments not valid.")
        
    def get_final_string(self):
        return self._final_string
        