import sys, os, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from participant import Participant
from utils.bash_util import execute_command
from utils.commands_util import commands
from utils.pseudorandom_util import hash_concat_data_and_known_rand
from utils.certificates_util import extract_public_key
from merkle import verify_proof
from utils.keys_util import verify_ECDSA, gen_ECDSA_keys, sign_ECDSA, concatenate
from utils.hash_util import compute_hash_from_data
from utils.pseudorandom_util import rand_extract
from blockchain import Blockchain
import random

class Bingo(Participant):
    
    """ 
    This class represents the sala bingo.
    """
    
    __slots__ = ['_known_CAs', '_GPs', '_SK', '_PK', '_final_string', '_blockchain', '_players_info', '_last_id', '_last_auth_id','_current_commitment_block','_current_opening_block', '_winner_id', '_folder']
    
    def __init__(self, folder):
        Participant.__init__(self)
        self._folder = folder+"/Bingo/"
        self._blockchain = None
        execute_command(commands["create_directory"](self._folder))
        execute_command(commands["copy_cert"](folder+"/AS/auto_certificate.cert", self._folder+"AS.cert"))
        self._known_CAs = [self._folder+"AS.cert"]
        self._GPs = {}
        self._players_info = {}
        self._final_string = None
        gen_ECDSA_keys("prime256v1", self._folder+"params.pem", self._folder+"private_key.pem", self._folder+"public_key.pem")
        self._SK = self._folder+"private_key.pem"
        self._PK = self._folder+"public_key.pem"
        self._last_id = 0
        self._last_auth_id = 0
        self._current_commitment_block = None
        self._current_opening_block = None
        self._winner_id = None
        self._game_code = str(random.randint(0,1000000))
        
    def get_folder(self):
        """
        Get the folder.
        # Returns
            string
                The folder.
        """
        return self._folder
        
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
        
        # Returns
            list of tuples (id_player, path_PK)
        """
        if len(self._players_info) == 0:
            raise Exception("No players info")
        
        data = {}
        for id in self._players_info.keys():
            data[id] = self._players_info[id]['BC_PK']
        
        self._blockchain.add_block('pre_game', self._game_code, data)
        
    # AUTHENTICATION
    def __init_player(self):
        """ 
        Initialize the player.
        """
        self._last_id += 1
        # blocks = True if self._blockchain is not None else False 
        return str(self._game_code), str(self._last_id-1), self._blockchain

    
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

        #return True
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
    
    def start_game(self):
        """ 
        Start the game.
        # Returns
            boolean
                True if the game is started, False otherwise.
        """
        # Inizializzo la PRF per il calcolo dei contributi casuali
        self._player_id = str(self._last_id)
        self._last_id += 1
         
        #self._round = 0
        
        self._IV = int(rand_extract(self._security_param, "hex"), 32) # Cast to a 32-bit integer cause it's used as a counter
        self._seed = rand_extract(self._security_param, "base64")
        
        #super().generate_message(self._SK, "Bingo")
        
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
        extract_public_key(self._GPs[self._players_info[id]['auth_id']], self._folder+"GP_PK.pem")
        with open(self._folder+"concat.txt", "w") as f:
            f.write(concat)
        if verify_ECDSA(self._folder+"GP_PK.pem", self._folder+"concat.txt", signature):
            # compute the signature of the sala bingo on all of them
            concat += signature
            with open(self._folder+"concat.txt", "w") as f:
                f.write(concat)
            sign_ECDSA(self._SK, self._folder+"concat.txt", self._folder+"signature.pem")
            return self._folder+"signature.pem"
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

        # the server adds its own paramsa, commitment and signature
        self._players_info[str(self._player_id)] = {}
        self._players_info[str(self._player_id)]["params"] = self._last_message[0]
        self._players_info[str(self._player_id)]["commitment"] = self._last_message[1]
        self._players_info[str(self._player_id)]["signature"] = self._last_message[2]
        
        concat = concatenate(*self._last_message[0], self._last_message[1])
        self._players_info[str(self._player_id)]["concat_1"] = concat
        
        concat = ""
        ids = list(self._players_info.keys())
        ids.sort()
        
        for id in ids:
            concat += self._players_info[id]["concat_1"]# params + commitment

        with open(self._folder+"concat.txt", "w") as f:
            f.write(concat) 

        sign_ECDSA(self._SK, self._folder+"concat.txt", self._folder+"signature.pem")
        
        pairs = []

        for id in ids:
            pairs.append((self._players_info[id]["params"], self._players_info[id]["commitment"]))
        
        if self._blockchain is not None:
            # send commit block
            # dict {player_id: (commitment, params, signature_path)}
            data = {}
            for id in self._players_info.keys():
                data[id] = (self._players_info[id]["params"], self._players_info[id]["commitment"], self._players_info[id]["signature"])
            if self._current_opening_block is not None:
                self._current_opening_block = None
            if self._current_commitment_block is None:
                self._current_commitment_block = self._blockchain.add_block('commit', self._game_code, data)
            return self._current_commitment_block, ""
        else:
            return pairs, self._folder+"signature.pem"
    
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
        self._players_info[str(self._player_id)]["opening"] = {"contribution": self._last_contribute, "randomness": self._last_randomess}
        
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
                
            with open(self._folder+"concat.txt", "w") as f:
                f.write(concat)
            sign_ECDSA(self._SK, self._folder+"concat.txt", self._folder+"signature.pem")
            self._final_string = self.__compute_final_string()
            
            if self._blockchain != None:
                # send openings block
                # dict {player_id: (randomness, contribution)}
                data = {}
                for id in self._players_info.keys():
                    data[id] = (self._players_info[id]["opening"]["contribution"], self._players_info[id]["opening"]["randomness"])
                if self._current_commitment_block is not None:
                    self._current_commitment_block = None
                if self._current_opening_block is None:
                    self._current_opening_block = self._blockchain.add_block('reveal',self._game_code, data)
                return self._current_opening_block , ""
            else:
                return openings, self._folder+"signature.pem"
        else:
            raise Exception("Commitments not valid.")
        
    def get_final_string(self):
        """ 
        Returns the final string.
        """
        return self._final_string
    
    def receive_mapping(self, player_id, mapping):
        # Verify signature with the original PK of the player
        extract_public_key(self._GPs[self._players_info[player_id]['auth_id']],self._folder+"GP_PK.pem")
        with open(self._folder+"concat.txt", "w") as f:
            f.write(concatenate(*mapping[0]))
        
        if verify_ECDSA(self._folder+"GP_PK.pem", self._folder+"concat.txt", mapping[1]):
            # Verify that the mapping is valid, i.e. verify that signature
            # of the player on the mapping is correctly computed
            new_pk = mapping[0][0]
            with open(self._folder+"concat.txt", "w") as f:
                f.write('')
            if verify_ECDSA(new_pk, self._folder+"concat.txt", mapping[0][1]):
                self._players_info[player_id]["BC_PK"] = new_pk
                
    def choose_winner(self):
        """
        Randomly choose a winner for this match and return it.
        # Returns
            tuple: (winner_id, game_code, bingo_signature)
                The id, the public key and the signature of the bingo on the winner.
        """
        ids = list(self._players_info.keys())
        self._winner_id = random.choice(ids)
        
        concat = self._winner_id + self._game_code
        with open(self._folder+"concat.txt", "w") as f:
            f.write(concat)
            
        sign_ECDSA(self._SK, self._folder+"concat.txt", self._folder+"signature.pem")

        return (self._winner_id, self._folder+"signature.pem")
    
    def end_game(self, *signs):
        """ 
        End the game and publish the winner.
        # Arguments
            signs: list
                The list of signatures of the players on the winner.
        # Raises
            Exception: If the number of signatures is not enough.
        """
        
        signs = list(*signs)
        signs.append((self._player_id, self._folder+"signature.pem"))

        if len(signs) < len(self._players_info):
            raise Exception("Not enough signatures")
        
        self._players_info[self._player_id]["BC_PK"] = self._PK
        
        sign_dict = {}
        for sign in signs:
            print(self._players_info[sign[0]]["BC_PK"])
            if not verify_ECDSA(self._players_info[sign[0]]["BC_PK"],self._folder+"concat.txt", sign[1]):
                raise Exception("Invalid signature")
            sign_dict[sign[0]] = sign[1]
        
        data = {}
        ids = list(self._players_info.keys())
        for id in ids:
            data[id] = (self._winner_id, self._game_code, sign_dict[id])
        
        self._blockchain.add_block('end_game', self._game_code, data)