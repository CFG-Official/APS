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
        if bingo_PK is None:
            raise Exception("Bingo PK not set.")
        
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
        
        leaves = [] # list of leaves of the merkle tree
        indices = {} # map the properties (key) to the index of leaves list (value)
        proofs = {} # map the properties (key) to the merkle proof (value)

        index = 0 

        # Compute the commitment (aka the leaves of the merkle tree) for each field of the merkle tree
        for key, value in self.clear_fields.items():
            # append the hashed value of the concatenation between the value and the randomness
            leaves.append(hash_concat_data_and_known_rand(value[0],value[1]))
            indices[key] = index
            index += 1
            
        # verify the merkle proofs for each leaf
        for key in policy:
            if key in indices:
                proofs[key] = merkle_proof(leaves, indices[key])
            
        # delete from indices the keys that are not in the policy
        indices = {key: value for key, value in indices.items() if key in policy}

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
        if policy is None or len(policy) == 0:
            raise Exception("Policy not set.")
        
        # compute the merkle proofs for the leaves that are in the policy, and the indices of the leaves 
        proofs, indices = self.__compute_proofs(policy)
        # get the clear values of the leaves that are in the policy
        clear_values = {key: self.clear_fields[key] for key in policy} 

        return clear_values, proofs, indices    
    
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
        self.round = 0

        # Inizializzo la PRF per il calcolo dei contributi casuali
        self.IV = int(rand_extract(2*self.security_param, "hex"), 16) # Cast to a 16-bit integer cause it's used as a counter
        self.seed = rand_extract(2*self.security_param, "base64")

    def end_game(self):
        """ 
        End a game.
        """
        self.game_code = None
        self.player_id = None
        self.round = 0

        self.IV = None
        self.seed = None

    def set_game_code(self, game_code):
        """
        Set the game code.
        # Arguments
            game_code: string
                The game code.
        """
        if game_code < 0:
            raise Exception("Game code must be positive.")
        
        self.game_code = game_code

    def set_player_id(self, player_id):
        """
        Set the player id.
        # Arguments
            player_id: string
                The player id.
        """
        if player_id < 0:
            raise Exception("Player id must be positive.")

        self.player_id = player_id

    def __generate_message(self):
        """
        Generate the message to be sent to the sala bingo in commitment phase.
        # Returns
            message: tuple -> (params: tuple -> (player_id, game_code, round, timestamp),
                                comm: string 
                                signature: string)
                The message to be sent to the sala bingo.
        """
        # If no game is started, no message can be computed
        if self.game_code is None or self.player_id is None:
            raise Exception("Game code or player id not set. This player isn't in a game.")
        
        # Set the 
        self.round += 1 # Go to next round
        params = (self.player_id, self.game_code, str(self.round), str(datetime.datetime.now()))

        # Compute commitment for a certain round
        comm = self.__compute_commitment()

        # Sign the message made by params and commitment
        signature = self.__sign_message(concatenate(*list(params), *comm))

        self.last_message = (params, comm, signature)

        return self.last_message

    def __compute_commitment(self):
        """
        Extract randomly a contribution for a round and compute the commitment.
        # Returns
            commitment: string
                The commitment of the contribution.
        """
        # Compute the PRF output
        prf_output = execute_command(commands["get_prf_value"](self.seed, self.IV)).split('= ')[1].strip()
        # Update the IV
        self.IV = (self.IV + 1) % 2*self.security_param

        # Divide output in two equal parts: the first is the contribution, the second is the randomness used to commit
        self.last_contribute = prf_output[:len(prf_output)//2]
        self.last_randomess = prf_output[len(prf_output)//2:]

        return compute_hash_from_data(self.last_contribute + self.last_randomess)
    
    def __sign_message(self, message):
        """
        Sign a message.
        # Arguments
            message: string
                The message to be signed.
        # Returns
            signature: string
                The signature of the message.
        """
        if message is None:
            raise Exception("Message is None. Can't sign a None message.")

        # Write the message in a file
        base_filename = self.user_name+'/'+self.user_name
        sign_filename = base_filename + '_comm_sign.pem'
        temp_filename = base_filename + "temp.txt"
        
        with open(temp_filename, "w") as f:
            f.write(message)

        # Sign the message contained in that file
        sign_ECDSA(self.SK, temp_filename, sign_filename)
        return sign_filename
    
    def send_commitment(self): # Nome da cambiare, non è solo il commitment
        """
        The player computes the message for commitment phase (including commit of contribute and other params), 
        then computes the signature on that message.
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
        The player receives the signature of the sala bingo on the commit-phase.
        Then it verifies the signature using the public key of the sala bingo.
        # Returns
            true if the signature is valid, false otherwise.
        """
        if signature is None:
            raise Exception("Signature not received.")

        temp_filename = self.user_name+'/'+self.user_name+"_temp.txt"

        with open(temp_filename, "w") as f: 
            f.write(concatenate(*self.last_message[0], self.last_message[1], self.last_message[2]))
        
        if verify_ECDSA(self._bingo_PK, temp_filename, signature):
            self._bingo_sign_on_comm = signature
            return True
        
        return False
    
    def receive_commitments_and_signature(self, pairs, signature):
        """
        The player receives the commitments, the parameters of other player
        and the signature of the sala bingo on them. 
        Then it verifies the server signature.
        
        # Arguments
            pairs: list
                The list of pairs.
            signature: string
                The signature of the sala bingo on the list of pairs concatenated.
                
        # Returns
            true if the signature is valid, false otherwise.
        """
        if pairs is None or signature is None:
            raise Exception("Commit pairs or signature are None.")

        temp_filename = self.user_name+'/'+self.user_name+"_temp.txt"
        
        self._contr_comm = pairs

        concat = ""
        for pair in pairs:
            for param in pair[0]:
                concat += param
            concat += pair[1]
        
        with open(temp_filename, "w") as f:
            f.write(concat)

        # Verify that the received signature is valid
        if verify_ECDSA(self._bingo_PK, temp_filename, signature):
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
        """
        Compute the final string constructed by the concatenation of all the openings sorted by player ID.
        # Returns
            final_string: string
                The final string.
        """
        # hash the concatenation of all the openings
        concat = ""
        for opening in self._contr_open:
            concat += opening[0]
        return compute_hash_from_data(concat)
    
    def __verify_commitments(self):
        """
        Verify that the commitments received really contains openings receivede.
        # Returns
            true if the commitments are valid, false otherwise.
        """

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
        if openings is None or signature is None:
            raise Exception("Openings or signature are None.")

        self._contr_open = openings
        
        temp_filename = self.user_name+'/'+self.user_name+"_temp.txt"

        if self.__verify_commitments():
            # Compute the concatenation of commit messages and openings messages in order
            # to verify the signature of sala bingo
            concat = ""
            for contr, opening in zip(self._contr_comm, self._contr_open):
                concat += concatenate(*contr[0], contr[1], opening[0], opening[1])
            with open(temp_filename, "w") as f:
                f.write(concat)

            # Verify the signature of sala bingo
            res = verify_ECDSA(self._bingo_PK, temp_filename, signature)
            self._final_string = self.__compute_final_string()
            return res
        else:
            raise Exception("Commitments not valid.")
        
    def get_final_string(self):
        """
        Return the final string.
        # Returns
            final_string: string
                The final string computed for the last ended roung.
        """
        return self._final_string
        