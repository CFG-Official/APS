import sys, os, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from utils.bash_util import execute_command
from utils.commands_util import commands
from utils.pseudorandom_util import hash_concat_data_and_known_rand
from utils.certificates_util import extract_public_key
from merkle import verify_proof
from utils.keys_util import verify_ECDSA, gen_ECDSA_keys, sign_ECDSA, concatenate
from utils.hash_util import compute_hash_from_data
from blockchain import Blockchain
import random

class Bingo:
    
    """ 
    This class represents the sala bingo.
    """
    
    __slots__ = ['_known_CAs', '_GPs', '_SK', '_PK', '_final_string', '_blockchain', '_players_info', '_last_id', '_game_code', '_last_auth_id']
    
    def __init__(self):
        self._blockchain = None
        execute_command(commands["create_directory"]("Bingo"))
        execute_command(commands["copy_cert"]("AS/auto_certificate.cert", "Bingo/AS.cert"))
        self._known_CAs = ["Bingo/AS.cert"]
        self._GPs = {}
        self._players_info = {}
        self._final_string = None
        gen_ECDSA_keys("prime256v1", "Bingo/params.pem", "Bingo/private_key.pem", "Bingo/public_key.pem")
        self._SK = "Bingo/private_key.pem"
        self._PK = "Bingo/public_key.pem"
        self._last_id = 0
        self._last_auth_id = 0
        self._game_code = random.randint(0,1000000)
        
    # BLOCKCHAIN VERSION
    def get_blockchain(self):
        """
        Get the blockchain.
        # Returns
            Blockchain
                The blockchain.
        """
        if self._blockchain is None:
            raise Exception("Blockchain is None")
        return self._blockchain
    
    def set_blockchain(self):
        """
        Set the blockchain.
        # Arguments
            blockchain: Blockchain
                The blockchain.
        """
        if self._blockchain is not None:
            raise Exception("Blockchain is already present")
        self._blockchain = Blockchain(self._PK,self._SK)
        
    def add_pre_game_block(self):
        """ 
        Add the pre-game block to the blockchain.
        """
        if len(self._players_info) == 0:
            raise Exception("No players info")
        self._blockchain.add_block('pre_game', self._players_info)
        
    # AUTHENTICATION
    def __init_player(self):
        """ 
        Initialize the player.
        """
        self._last_id += 1
        return str(self._game_code), str(self._last_id-1)
    
    def get_PK(self):
        """
        Get the public key of the sala bingo.
        # Returns
            string
                The public key of the sala bingo.
        """

        return self._PK
        
    def __check_CA(self, GP_cert, CA_cert):
        """ 
        Check if the CA is known.
        # Arguments
            GP_cert: string
                The name of the GP certificate file.
            CA_cert: string
                The name of the CA certificate file.
        # Returns
            boolean
                True if the CA is known, False otherwise.
        """

        issuer = execute_command(commands["cert_extract_issuer"](GP_cert))
        subject = execute_command(commands["cert_extract_subject"](CA_cert))

        known_subjects = [execute_command(commands["cert_extract_subject"](CA)) for CA in self._known_CAs]
        return issuer == subject
        
    def __check_sign(self, GP_cert, AS_cert):
        """ 
        Check if the sign is valid.
        # Arguments
            GP_cert: string
                The name of the GP certificate file.
            CA_cert: string 
                The name of the CA certificate file.
        # Returns   
            boolean
                True if the sign is valid, False otherwise.
        """

        res = execute_command(commands["validate_certificate"](AS_cert, GP_cert)).split(" ")[1].replace("\n", "").replace(" ", "")
        return True if res == "OK" else False
    
    def __check_expiration(self, GP_cert):
        """ 
        Check if the GP is expired.
        # Arguments
            GP_cert: string
                The name of the GP certificate file.
        # Returns
            boolean
                True if the GP is not expired, False otherwise.
        """

        expiration_date = execute_command(commands["cert_extract_expiration_date"](GP_cert)).split("=")[1]
        expiration_date = datetime.datetime.strptime(expiration_date.removesuffix("\n"), "%b %d %H:%M:%S %Y %Z")
        current_date = datetime.datetime.now()
        days_left = (expiration_date - current_date).days

        return True if days_left > 0 else False
    
    def receive_GP(self, GP):
        """ 
        Receive the GP from the user.
        # Arguments
            GP: string
                The name of the GP certificate file.
        # Returns
            boolean
                True if the GP is valid, False otherwise.
        """
        if GP is None:
            raise Exception("GP is None")

        if self.__check_CA(GP, self._known_CAs[0]) and self.__check_expiration(GP) and self.__check_sign(GP, self._known_CAs[0]):
            self._last_auth_id += 1
            # self._GPs.append(GP
            self._GPs[self._last_auth_id] = GP
            return self._last_auth_id
        return None
    
    def __extract_root(self, GP_cert):
        """
        Extract the root from the GP certificate.
        # Arguments
            GP_cert: string
                The name of the GP certificate file.
        # Returns
            string
                The root of the GP certificate.
        """

        text = execute_command(commands["cert_extract_merkle_root"](GP_cert))
        
        # find the 'X509v3 Subject Alternative Name:' string and extract the root
        return text.split("X509v3 Subject Alternative Name:")[1].split("DNS:")[1].split("\n")[0].encode('utf-8').decode('unicode_escape')

    def __validate_clear_fields(self, policy, clear_fields, proofs, indices, auth_id):
        """
        Perform a validation of the clear fields sent by the user.

        # Arguments
            policy: list
                The policy of the DPA.
            clear_fields: dict
                The clear fields sent by the user. key: field name, value: (value, randomness)
            proofs: dict
                The merkle proofs of the clear fields. key: field name, value: list of hashes
            indices: dict
                The indices of the clear fields.
        # Returns
            boolean
                True if the clear fields are valid, False otherwise. 
        """

        # length check
        if len(policy) != len(clear_fields):
            raise Exception("Policy and clear fields have different lengths")
        
        # key check
        for item in policy:
            if item not in clear_fields.keys():
                raise Exception("Policy and clear fields have different keys")
            
        # root = self.__extract_root(self._GPs[0]) # vedi se va bene cosi
        root = self.__extract_root(self._GPs[auth_id])

        # value check with merkle proofs
        leaves = {}
        for key, value in clear_fields.items():
            # append the hashed value of the concatenation between the value and the randomness
            leaves[key] = hash_concat_data_and_known_rand(value[0],value[1])
            
        # check for the proofs of the clear fields
        for key, value in proofs.items():
            res = verify_proof(root, value, leaves[key], indices[key])
            if not res:
                print("Proofs are not valid")
                raise Exception("Invalid proof")
            
        self._players_info[str(self._last_id)] = {}
        self._players_info[str(self._last_id)]['auth_id'] = auth_id
        
        return self.__init_player()

    def receive_clear_fields(self,policy,clear_fields, proofs, indices, auth_id):
        """
        Receive the clear fields from the user.
        # Arguments
            policy: list
                The policy of the DPA.
            clear_fields: dict
                The clear fields sent by the user. key: field name, value: (value, randomness)
            proofs: dict
                The merkle proofs of the clear fields. key: field name, value: list of hashes
            indices: dict
                The indices of the clear fields.
        # Returns
            boolean
                True if the clear fields are valid, False otherwise.
        """
        # verify if the keys of clear fields and the policy are the same
        return self.__validate_clear_fields(policy,clear_fields, proofs, indices, auth_id)
        
    # GAME
        
    def receive_commitment(self, params, commitment, signature):
        """ 
        The sala bingo receives the commitment, the signature and the 
        additional parameters from the user. It verifies the signature
        of the user on the commitment and the additional parameters.
        If it is valid, it computes its signature on all of them and 
        returns it to the user.
        # Arguments
            params: tuple
                The list of additional parameters.
            commitment: string
                The commitment.
            signature: string
                The signature of the user on the commitment and the additional parameters.
        # Returns
            signature: string
                The signature of the sala bingo on the additional parameters and the commitment.
        """
        # concatenate params and commitment
        id = params[0][0]
        concat = concatenate(*params, commitment)
        self._players_info[id]["params"] = params
        self._players_info[id]["commitment"] = commitment
        self._players_info[id]["signature"] = signature
        self._players_info[id]["concat_1"] = concat

        # verify the signature of the user on the commitment and the additional parameters
        # using the PK contained in the GP certificate
        extract_public_key(self._GPs[self._players_info[id]['auth_id']], "Bingo/GP_PK.pem")
        with open("Bingo/concat.txt", "w") as f:
            f.write(concat)
        if verify_ECDSA("Bingo/GP_PK.pem", "Bingo/concat.txt", signature):
            # compute the signature of the sala bingo on all of them
            concat += signature
            with open("Bingo/concat.txt", "w") as f:
                f.write(concat)
            sign_ECDSA(self._SK, "Bingo/concat.txt", "Bingo/signature.pem")
            return "Bingo/signature.pem"
        return None
            
    def publish_commitments_and_signature(self):
        """ 
        Once it has received all the commitments, the sala bingo publishes
        them and its signature on them.
        
        # Returns
            commitments: list
                The list of (params, commitment).
            signature: string
                The signature of the sala bingo on the concatenation between the params
                and the commitment.
        """
        concat = ""
        ids = list(self._players_info.keys())
        ids.sort()
        
        for id in ids:
            concat += self._players_info[id]["concat_1"]# params + commitment

        with open("Bingo/concat.txt", "w") as f:
            f.write(concat) 

        sign_ECDSA(self._SK, "Bingo/concat.txt", "Bingo/signature.pem")
        
        pairs = []
        ids = list(self._players_info.keys())
        ids.sort()
        for id in ids:
            pairs.append((self._players_info[id]["params"], self._players_info[id]["commitment"]))

        return pairs, "Bingo/signature.pem"
    
    def receive_opening(self, id, contribution, randomness):
        """ 
        The sala bingo receives the opening from the user.
        """
        # append the opening to the list of openings
        self._players_info[id]["opening"] = {"contribution": contribution, "randomness": randomness}
        
    def __compute_final_string(self):
        """
        Compute the final string based on the concatenation of all the openings.

        # Returns
            string
                The final string.
        """
        # hash the concatenation of all the openings
        concat = ""
        ids = list(self._players_info.keys())
        ids.sort()
        
        for id in ids:
            concat += self._players_info[id]["opening"]["contribution"]
        
        return compute_hash_from_data(concat)

    def __verify_commitments(self):
        """
        Verify the commitments received from the user.
        # Returns
            boolean
                True if the commitments are valid, False otherwise.
        """
        # verify the commitments
        
        ids = list(self._players_info.keys())
        ids.sort()
        for id in ids:
            if self._players_info[id]["commitment"] != hash_concat_data_and_known_rand(self._players_info[id]["opening"]["contribution"], self._players_info[id]["opening"]["randomness"]):
                return False

        return True

    def publish_openings(self):
        """ 
        Once received all the openings, the sala bingo computes the
        final string and publishes the openings as (message, randomness) 
        pairs.
        In addition it computed and returns the signature on the concatenation
        of all the commitments and the opensings.   
        # Returns
            openings: list
                The list of (message, randomness) pairs.
            signature: string
                The signature of the sala bingo on the concatenation of all the commitments
                and the openings.
        """
        openings = []
        ids = list(self._players_info.keys())
        ids.sort()
        
        for id in ids:
            openings.append((self._players_info[id]["opening"]["contribution"], self._players_info[id]["opening"]["randomness"]))
            
        if self.__verify_commitments():
            concat = ""
            
            ids = list(self._players_info.keys())
            ids.sort()
            for id in ids:
                concat += self._players_info[id]["concat_1"]
                concat += self._players_info[id]["opening"]["contribution"] + self._players_info[id]["opening"]["randomness"]
                
            with open("Bingo/concat.txt", "w") as f:
                f.write(concat)
            sign_ECDSA(self._SK, "Bingo/concat.txt", "Bingo/signature.pem")
            self._final_string = self.__compute_final_string()
            return openings, "Bingo/signature.pem"
        else:
            raise Exception("Commitments not valid.")
        
    def get_final_string(self):
        """ 
        Returns the final string.
        """
        return self._final_string
    
    def receive_mapping(self, player_id, mapping):
        # Verify signature with the original PK of the player
        extract_public_key(self._GPs[self._players_info[player_id]['auth_id']], "Bingo/GP_PK.pem")
        with open("Bingo/concat.txt", "w") as f:
            f.write(concatenate(*mapping[0]))
        
        if verify_ECDSA("Bingo/GP_PK.pem", "Bingo/concat.txt", mapping[1]):
            # Verify that the mapping is valid, i.e. verify that signature
            # of the player on the mapping is correctly computed
            new_pk = mapping[0][0]
            with open("Bingo/concat.txt", "w") as f:
                f.write('')
            if verify_ECDSA(new_pk, "Bingo/concat.txt", mapping[0][1]):
                self._players_info[player_id]["BC_PK"] = new_pk
                
