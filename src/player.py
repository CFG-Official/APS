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
from src.utils.keys_util import *
from blocks import *

class Player(User):
    
    """ 
    This class represents a player of the bingo game, it inherits from the User class.
    """
        
    __slots__ = ['_game_code', '_player_id', '_round', '_seed', '_IV', '_security_param', '_final_string', '_contr_comm', '_contr_open', '_last_message', '_last_contribute', '_last_randomness', '_SK_BC', '_PK_BC', '_blockchain', '_state', '_last_opening']

    def __init__(self, CIE_fields):
        super().__init__(CIE_fields)
        self._game_code = None
        self._player_id = None
        self._round = 0
        self._auth_id = None
        self._last_message = None
        self._seed = None
        self._IV = None
        self._last_contribute = None
        self._last_randomess = None
        self._security_param = 32 # (in bytes) -> 256 bits
        self._contr_comm = []
        self._contr_open = []
        self._state = []
        self._final_string = None
    
    # AUTHENTICATION

    def send_GP(self):
        """ 
        Send the GP certificate to the sala bingo.
        # Returns
            GP_certificate: string
                The name of the GP certificate file.
        """
        return self._GP_certificate

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

    def set_auth_id(self, auth_id):
        """ 
        Set the authentication id.
        # Arguments
            auth_id: string
                The authentication id.
        """
        if auth_id is None:
            raise Exception("Authentication id not set.")
        
        self._auth_id = auth_id

    def get_auth_id(self):
        """ 
        Get the authentication id.
        # Returns
            auth_id: string
                The authentication id.
        """
        return self._auth_id
    
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
        for key, value in self._clear_fields.items():
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
        clear_values = {key: self._clear_fields[key] for key in policy} 

        return clear_values, proofs, indices    
    
    # GAME    

    def start_game(self, game_code, player_id, blockchain = None):
        """ 
        Start a game.
        # Arguments
            game_code: string
                The game code.
            player_id: string
                The player id.
        """
        self._blockchain = blockchain
        self.set_game_code(game_code)
        self.set_player_id(player_id)
        self._round = 0

        # Inizializzo la PRF per il calcolo dei contributi casuali
        self._IV = int(rand_extract(self._security_param, "hex"), 32) # Cast to a 32-bit integer cause it's used as a counter
        self._seed = rand_extract(self._security_param, "base64")

    def end_game(self):
        """ 
        End a game.
        """
        self._game_code = None
        self._player_id = None
        self._round = 0

        self._IV = None
        self._seed = None

    def set_game_code(self, game_code):
        """
        Set the game code.
        # Arguments
            game_code: string
                The game code.
        """
        if game_code is None:
            raise Exception("Game code not set.")
                
        self._game_code = game_code

    def set_player_id(self, player_id):
        """
        Set the player id.
        # Arguments
            player_id: string
                The player id.
        """
        if player_id is None:
            raise Exception("Player id not set.")

        self._player_id = player_id

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
        if self._game_code is None or self._player_id is None:
            raise Exception("Game code or player id not set. This player isn't in a game.")
        
        # Set the 
        self._round += 1 # Go to next round
        params = (self._player_id, self._game_code, str(self._round), str(datetime.now()))

        # Compute commitment for a certain round
        comm = self.__compute_commitment()

        # Sign the message made by params and commitment
        signature = self.__sign_message(concatenate(*list(params), *comm))

        self._last_message = (params, comm, signature)

        return self._last_message

    def __compute_commitment(self):
        """
        Extract randomly a contribution for a round and compute the commitment.
        # Returns
            commitment: string
                The commitment of the contribution.
        """
        # Compute the PRF output
        prf_output = execute_command(commands["get_prf_value"](self._seed, self._IV)).split('= ')[1].strip()
        # Update the IV
        self._IV = (self._IV + 1) % (self._security_param)

        # Divide output in two equal parts: the first is the contribution, the second is the randomness used to commit
        self._last_contribute = prf_output[:len(prf_output)//2]
        self._last_randomess = prf_output[len(prf_output)//2:]

        return compute_hash_from_data(self._last_contribute + self._last_randomess)
    
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
        
        temp_filename = self._user_name+'/'+self._user_name+"_temp.txt"
        sign_filename = self._user_name+'/'+self._user_name+'_comm_sign.pem'

        with open(temp_filename, "w") as f:
            f.write(message)

        # sign the message
        sign_ECDSA(self._SK_GP, temp_filename, sign_filename)
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

        temp_filename = self._user_name+'/'+self._user_name+"_temp.txt"

        with open(temp_filename, "w") as f: 
            f.write(concatenate(*self._last_message[0], self._last_message[1], self._last_message[2]))
        
        if verify_ECDSA(self._bingo_PK, temp_filename, signature):
            self._bingo_sign_on_comm = signature
            return True
        
        return False
    
    def receive_commitments_and_signature(self, pairs, signature = None, block = None):
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
        temp_filename = self._user_name+'/'+self._user_name+"_temp.txt"
        
        if self._blockchain is None:

            if pairs is None or signature is None:
                raise Exception("Commit pairs or signature are None.")

            self._contr_comm = pairs

            concat = ""
            for pair in pairs:
                for param in pair[0]:
                    concat += param
                concat += pair[1]
            
            with open(temp_filename, "w") as f:
                f.write(concat)

            # Verify that the received signature is valid
            if not verify_ECDSA(self._bingo_PK, temp_filename, signature):
                self._bingo_sign_on_comm = signature
                raise Exception("Bingo's signature on the commit pairs is not valid.")
            
            return True
        
        else:
            # PROCESS BLOCK
            
            # verify player's signature on its own pair
            data = pairs.get_data()
            
            if self._player_id not in data.keys():
                raise Exception("Player's id not in the block.")
            
            my_pair = data[self._player_id]
            concat = concatenate(*my_pair[0], my_pair[1])
            
            with open(temp_filename, "w") as f:
                f.write(concat)
                
            if not verify_ECDSA(self._PK_GP, temp_filename, my_pair[2]):
                raise Exception("Player's signature on its own pair is not valid.")
            
            # verify bingo's signature on the block
            if not pairs.verify_block(self._bingo_PK):
                raise Exception("Bingo's signature on the block is not valid.")
            
            # if all is ok, add the block to the player's state
            self._state.append(pairs)
            return True
    
    def send_opening(self):
        """ 
        The player sends its opening to the sala bingo.
        # Returns
            opening: string
                The opening as (message, randomness) pair.
        """
        self._last_opening = (self._last_contribute, self._last_randomess)
        return self._player_id, *self._last_opening

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
            res = hash_concat_data_and_known_rand(opening[0], opening[1])
            if contr[1] != res:
                return False
        return True
    
    def receive_openings(self, openings, signature = None):
        """ 
        The player receives the openings from the sala bingo and computes
        the final string.
        # Arguments
            openings: list
                The list of openings (message, randomness).
        """
        if self._blockchain is None:
            
            if openings is None or signature is None:
                raise Exception("Openings or signature are None.")

            self._contr_open = openings
            
            temp_filename = self._user_name+'/'+self._user_name+"_temp.txt"

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
        
        else:
            # PROCESS BLOCK
            
            # verify bingo's signature on the block
            if not openings.verify_block(self._bingo_PK):
                raise Exception("Bingo's signature on the block is not valid.")

            ids = list(openings.get_data().keys())
            ids.sort()
            for id in ids:
                self._contr_open.append(openings.get_data()[id])
                
            ids = list(self._state[-1].get_data().keys())
            ids.sort()
            for id in ids:
                self._contr_comm.append(self._state[-1].get_data()[id])
            
            # verify commitments openings 
            if self.__verify_commitments():
                            
                # if all is ok, add the block to the player's state
                self._state.append(openings)
            
                # compute final string
                self._final_string = self.__compute_final_string()
                
            else:
                
                raise Exception("Commitments not valid.")
            
            return True
        
    def get_final_string(self):
        """
        Return the final string.
        # Returns
            final_string: string
                The final string computed for the last ended roung.
        """
        return self._final_string
        
    def generate_mapping(self):
        """
        Generate a message containg a new public key with a signature using
        the new private key (Fiat Shamir 86).
        """

        # Generate a new key pair using ECDSA
        print("Generating new key pair for mapping...")
        base_filename = self._user_name+'/'+ 'BC_mapping_'
        self._SK_BC = base_filename + 'private_key.pem'
        self._PK_BC = base_filename + 'public_key.pem'
        gen_ECDSA_keys('prime256v1', base_filename + 'param.pem', self._SK_BC, self._PK_BC)
        
        # Fiat-Shamir 86 protocol with mapping key
        print("Generating signature for mapping...")
        signature_bc = self._user_name+'/'+self._user_name+'_BC_mapping_sign.pem'
        with open(self._user_name + "/void_file.txt", "w") as f:
                f.write('')
        sign_ECDSA(self._SK_BC, self._user_name + "/void_file.txt", signature_bc)
        temp = (self._PK_BC, signature_bc)

        # Shnorr signature with GP key
        print("Generating signature for mapping...")
        signature_gp = self._user_name+'/'+self._user_name+'_GP_mapping_sign.pem'
        with open(self._user_name + "/_temp_sign_mapping.txt", "w") as f:
                f.write(concatenate(*temp))
        sign_ECDSA(self._SK_GP, self._user_name + "/_temp_sign_mapping.txt", signature_gp)

        return temp, signature_gp

    def contestate_opening(self):

        if self._blockchain is None:
            raise Exception("There is no blockchain to contestate.")
        
        self._blockchain.set_credentials(self._PK_BC, self._SK_BC)
        self._blockchain.add_block("dispute", {self._player_id: self._last_opening})
        self._blockchain.reset_server_credentials()

    def contestate_commit(self):

        if self._blockchain is None:
            raise Exception("There is no blockchain to contestate.")
        
        self._blockchain.set_credentials(self._PK_BC, self._SK_BC)
        self._blockchain.add_block("dispute", {self._player_id: self._last_contribute})
        self._blockchain.reset_server_credentials()