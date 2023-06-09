import sys, os, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from user import User
from merkle import merkle_proof
from utils.pseudorandom_util import hash_concat_data_and_known_rand

class Player(User):
    
    """ 
    This class represents a player of the bingo game, it inherits from the User class.
    """
    
    # AUTHENTICATION
    
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
    
    # GAME
    
    def send_commitment(self):
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
        return self._params, self.__compute_commitment(), self.__sign_message()
    
    def recieve_signature(self, signature):
        """ 
        The player receives the signature of the sala bingo on the commitment,
        the signature and the additional parameters. Then it verifies the 
        signature.
        # Returns
            true if the signature is valid, false otherwise.
        """
        pass
    
    def recieve_commitments_and_signature(self, values, signature):
        """
        The player receives the commitments, the parameters and the 
        signature of the sala bingo on them. Then it verifies the 
        signature.
        
        # Arguments
            values: list
                The list of values.
            signature: string
                The signature of the sala bingo on the commitments.
                
        # Returns
            true if the signature is valid, false otherwise.
            
        """
        pass
    
    def send_opening(self):
        """ 
        The player sends its opening to the sala bingo.
        # Returns
            opening: string
                The opening as (message, randomness) pair.
        """
        pass
    
    def recieve_openings(self, openings):
        """ 
        The player receives the openings from the sala bingo and computes
        the final string.
        # Arguments
            openings: list
                The list of openings.
        """
        pass
