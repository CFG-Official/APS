import datetime, random,os
from participant import Participant
from blockchain import Blockchain
from merkle import verify_proof
from utils.bash_util import execute_command
from utils.commands_util import commands
from utils.hash_util import compute_hash_from_data
from utils.pseudorandom_util import hash_concat_data_and_known_rand, rand_extract
from utils.certificates_util import extract_public_key
from utils.keys_util import verify_ECDSA, gen_ECDSA_keys, sign_ECDSA, concatenate


class Bingo(Participant):
    __base_dir = "Bingo"
    __cert_path = "AS/auto_certificate.cert"
    __cert_dir = os.path.join(__base_dir, "AS.cert")
    __key_patams_path = os.path.join(__base_dir, "params.pem")
    __private_key_path = os.path.join(__base_dir, "private_key.pem")
    __public_key_path = os.path.join(__base_dir, "public_key.pem")

    __slots__ = ['_known_CAs', '_GPs', '_SK', '_PK', '_final_string', '_blockchain', 
                 '_players_info', '_last_id', '_last_auth_id', '_current_commitment_block', 
                 '_current_opening_block', '_winner_id', '_game_code']
    
    def __init__(self):
        super().__init__()
        self._blockchain = None
        execute_command(commands["create_directory"](self.__base_dir))
        execute_command(commands["copy_cert"](self.__cert_path, self.__cert_dir))
        self._known_CAs = [self.__cert_dir]
        self._GPs = {}
        self._players_info = {}
        self._final_string = None
        gen_ECDSA_keys("prime256v1", self.__key_patams_path, self.__private_key_path, self.__public_key_path)
        self._SK = self.__private_key_path
        self._PK = self.__public_key_path
        self._last_id = 0
        self._last_auth_id = 0
        self._current_commitment_block = None
        self._current_opening_block = None
        self._winner_id = None
        self._game_code = str(random.randint(0, 1000000))


    def get_blockchain(self):
        """Return the blockchain. Raise exception if it is None."""
        if self._blockchain is None:
            raise Exception("Blockchain is None")
        return self._blockchain

    def set_blockchain(self):
        """Set the blockchain. Raise exception if it is already present."""
        if self._blockchain is not None:
            raise Exception("Blockchain is already present")
        self._blockchain = Blockchain(self._PK,self._SK)

    def add_pre_game_block(self):
        """Add pre game block to the blockchain. Raise exception if no player info."""
        if len(self._players_info) == 0:
            raise Exception("No players info")

        data = {id: info['BC_PK'] for id, info in self._players_info.items()}
        self._blockchain.add_block('pre_game', self._game_code, data)

    # other parts of your code...

    def __check_CA(self, GP_cert, CA_cert):
        """Check if issuer of GP_cert is the same as subject of CA_cert."""
        issuer = execute_command(commands["cert_extract_issuer"](GP_cert))
        subject = execute_command(commands["cert_extract_subject"](CA_cert))

        return issuer == subject in (execute_command(commands["cert_extract_subject"](CA)) for CA in self._known_CAs)

    def __check_sign(self, GP_cert, AS_cert):
        """Check if the signature is valid."""
        # TODO: Uncomment and use the real check when ready.
        # res = execute_command(commands["validate_certificate"](AS_cert, GP_cert)).split()[1].strip()
        # return res == "OK"
        return True

    def __check_expiration(self, GP_cert):
        """Check if the certificate is expired."""
        expiration_date_str = execute_command(commands["cert_extract_expiration_date"](GP_cert)).split("=")[1].strip()
        expiration_date = datetime.datetime.strptime(expiration_date_str, "%b %d %H:%M:%S %Y %Z")

        return (expiration_date - datetime.datetime.now()).days > 0
        
    # AUTHENTICATION
    def __init_player(self):
        self._last_id += 1
        # blocks = True if self._blockchain is not None else False 
        return str(self._game_code), str(self._last_id-1), self._blockchain

    
    def get_PK(self):
        return self._PK
        
    def receive_GP(self, GP):
        """Receive and check GP. Return the last auth id if GP is valid."""
        if GP is None:
            raise Exception("GP is None")

        if all([
            self.__check_CA(GP, self._known_CAs[0]),
            self.__check_expiration(GP),
            self.__check_sign(GP, self._known_CAs[0]),
        ]):
            self._last_auth_id += 1
            self._GPs[self._last_auth_id] = GP
            return self._last_auth_id
        else:
            return None

    
    def __extract_root(self, GP_cert):
        text = execute_command(commands["cert_extract_merkle_root"](GP_cert))
        
        # find the 'X509v3 Subject Alternative Name:' string and extract the root
        return text.split("X509v3 Subject Alternative Name:")[1].split("DNS:")[1].split("\n")[0].encode('utf-8').decode('unicode_escape')

    def __validate_clear_fields(self, policy, clear_fields, proofs, indices, auth_id):
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
        # verify if the keys of clear fields and the policy are the same
        return self.__validate_clear_fields(policy,clear_fields, proofs, indices, auth_id)
        
    # GAME
    
    def start_game(self):
        self._player_id = str(self._last_id)
        self._last_id += 1
         
        self._round = 0
        
        self._IV = int(rand_extract(self._security_param, "hex"), 32) # Cast to a 32-bit integer cause it's used as a counter
        self._seed = rand_extract(self._security_param, "base64")
        
        super().generate_message(self._SK, "Bingo")
        
    def receive_commitment(self, params, commitment, signature):
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

        with open("Bingo/concat.txt", "w") as f:
            f.write(concat) 

        sign_ECDSA(self._SK, "Bingo/concat.txt", "Bingo/signature.pem")
        
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
            return pairs, "Bingo/signature.pem"
    
    def receive_opening(self, id, contribution, randomness):
        # append the opening to the list of openings
        self._players_info[id]["opening"] = {"contribution": contribution, "randomness": randomness}
        
    def __compute_final_string(self):
        concat = ""
        ids = list(self._players_info.keys())
        ids.sort()
        
        for id in ids:
            concat += self._players_info[id]["opening"]["contribution"]
        
        return compute_hash_from_data(concat)

    def __verify_commitments(self):
        ids = list(self._players_info.keys())
        ids.sort()
        for id in ids:
            if self._players_info[id]["commitment"] != hash_concat_data_and_known_rand(self._players_info[id]["opening"]["contribution"], self._players_info[id]["opening"]["randomness"]):
                return False

        return True

    def publish_openings(self):
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
                
            with open("Bingo/concat.txt", "w") as f:
                f.write(concat)
            sign_ECDSA(self._SK, "Bingo/concat.txt", "Bingo/signature.pem")
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
                return openings, "Bingo/signature.pem"
        else:
            raise Exception("Commitments not valid.")
        
    def get_final_string(self):
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
                
    def choose_winner(self):
        ids = list(self._players_info.keys())
        self._winner_id = random.choice(ids)
        
        concat = self._winner_id + self._game_code
        with open("Bingo/concat.txt", "w") as f:
            f.write(concat)
            
        sign_ECDSA(self._SK, "Bingo/concat.txt", "Bingo/signature.pem")

        return (self._winner_id, "Bingo/signature.pem")
    
    def end_game(self, *signs):
        
        signs = list(*signs)
        signs.append((self._player_id, "Bingo/signature.pem"))

        if len(signs) < len(self._players_info):
            raise Exception("Not enough signatures")
        
        self._players_info[self._player_id]["BC_PK"] = self._PK
        
        sign_dict = {}
        for sign in signs:
            print(self._players_info[sign[0]]["BC_PK"])
            if not verify_ECDSA(self._players_info[sign[0]]["BC_PK"],"Bingo/concat.txt", sign[1]):
                raise Exception("Invalid signature")
            sign_dict[sign[0]] = sign[1]
        
        data = {}
        ids = list(self._players_info.keys())
        for id in ids:
            data[id] = (self._winner_id, self._game_code, sign_dict[id])
        
        self._blockchain.add_block('end_game', self._game_code, data)