import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from user import User
from participant import Participant
from merkle import merkle_proof
from utils.hash_util import compute_hash_from_data
from utils.keys_util import concatenate, sign_ECDSA, verify_ECDSA
from utils.pseudorandom_util import hash_concat_data_and_known_rand, rand_extract
from utils.hash_util import compute_hash_from_data
from src.utils.keys_util import *
from blocks import *

class Player(User, Participant):
    
    """ 
    This class represents a player of the bingo game, it inherits from the User class.
    """
        
    __slots__ = ['_final_string', '_contr_comm', '_contr_open', '_SK_BC', '_PK_BC', '_blockchain', '_state']

    def __init__(self, CIE_fields, folder):
        User.__init__(self,CIE_fields, folder)
        Participant.__init__(self)
        self._auth_id = None
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
        return super().generate_message(self._SK_BC, self._folder)
    
    def receive_signature(self, signature):
        """ 
        The player receives the signature of the sala bingo on the commit-phase.
        Then it verifies the signature using the public key of the sala bingo.
        # Returns
            true if the signature is valid, false otherwise.
        """
        if signature is None:
            raise Exception("Signature not received.")

        temp_filename = self._folder+self._user_name+"_temp.txt"

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
        temp_filename = self._folder+self._user_name+"_temp.txt"
        
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
                
            if not verify_ECDSA(self._PK_BC, temp_filename, my_pair[2]):
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
        # print("PLAYER: ", self._player_id)
        # print("ROUND ", self._round)
        for opening in self._contr_open:
            # print("CONCATENING: ", opening[0])
            concat += opening[0]
        self._contr_open.clear()
        self._contr_comm.clear()
        return compute_hash_from_data(concat)
    
    def __verify_commitments(self, contr_comm, contr_open):
        """
        Verify that the commitments received really contains openings receivede.
        # Returns
            true if the commitments are valid, false otherwise.
        """

        for contr, opening in zip(contr_comm, contr_open):
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
            
            temp_filename = self._folder+self._user_name+"_temp.txt"

            if self.__verify_commitments(self._contr_comm, self._contr_open):
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
            if self.__verify_commitments(self._contr_comm, self._contr_open):
                            
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
        base_filename = self._folder+ 'BC_mapping_'
        self._SK_BC = base_filename + 'private_key.pem'
        self._PK_BC = base_filename + 'public_key.pem'
        gen_ECDSA_keys('prime256v1', base_filename + 'param.pem', self._SK_BC, self._PK_BC)
        
        # Fiat-Shamir 86 protocol with mapping key
        print("Generating signature for mapping...")
        signature_bc = self._folder + self._user_name+'_BC_mapping_sign.pem'
        with open(self._folder + self._user_name + "_void_file.txt", "w") as f:
                f.write('')
        sign_ECDSA(self._SK_BC, self._folder + self._user_name + "_void_file.txt", signature_bc)
        temp = (self._PK_BC, signature_bc)

        # Shnorr signature with GP key
        print("Generating signature for mapping...")
        signature_gp = self._folder + self._user_name+'_GP_mapping_sign.pem'
        with open(self._folder + self._user_name + "_temp_sign_mapping.txt", "w") as f:
                f.write(concatenate(*temp))
        sign_ECDSA(self._SK_GP, self._folder + self._user_name + "_temp_sign_mapping.txt", signature_gp)

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
        
    def get_winner(self, winner_info):
        
        # winner_info = (winner_id, bingo_signature)
        concat = winner_info[0] + self._game_code

        with open(self._folder+ self._user_name +"_temp_winner.txt", "w") as f:
            f.write(concat)
        if verify_ECDSA(self._bingo_PK, self._folder + self._user_name +"_temp_winner.txt", winner_info[1]):
            sign_ECDSA(self._SK_BC,self._folder + self._user_name +"_temp_winner.txt", self._folder + self._user_name +"_temp_winner_sign.txt")
            return (self._player_id, self._folder + self._user_name +"_temp_winner_sign.txt")