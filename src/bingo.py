import sys, os, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from utils.bash_util import execute_command
from utils.commands_util import commands
from utils.pseudorandom_util import hash_concat_data_and_known_rand
from utils.certificates_util import extract_public_key
from merkle import merkle_proof, verify_proof
from utils.keys_util import verify_ECDSA, gen_ECDSA_keys, sign_ECDSA

class Bingo:
    
    """ 
    This class represents the sala bingo.
    """
    
    def __init__(self):
        execute_command(commands["create_directory"]("Bingo"))
        execute_command(commands["copy_cert"]("AS/auto_certificate.cert", "Bingo/AS.cert"))
        self.known_CAs = ["Bingo/AS.cert"]
        self.GPs = []
        gen_ECDSA_keys("prime256v1", "Bingo/params.pem", "Bingo/private_key.pem", "Bingo/public_key.pem")
        self.SK = "Bingo/private_key.pem"
        self.PK = "Bingo/public_key.pem"
        
    # AUTHENTICATION
        
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
        self.GPs.append(GP)
        if self.__check_CA(GP, self.known_CAs[0]) and self.__check_expiration(GP) and self.__check_sign(GP, self.known_CAs[0]):
            self.GPs.append(GP)
            return True
        return False
    
    def __extract_root(self, GP_cert):
        # extract the root from the GP certificate
        text = execute_command(commands["cert_extract_merkle_root"](GP_cert))
        # find the 'X509v3 Subject Alternative Name:' string and extract the root
        return text.split("X509v3 Subject Alternative Name:")[1].split("DNS:")[1].split("\n")[0].encode('utf-8').decode('unicode_escape')

    def __validate_clear_fields(self, policy, clear_fields, proofs, indices):
        
        # length check
        if len(policy) != len(clear_fields):
            return False
        
        # key check
        for item in policy:
            if item not in clear_fields.keys():
                return False
            
        root = self.__extract_root(self.GPs[0])
            
        # value check with merkle proofs
        leaves = {}
        for key, value in clear_fields.items():
            # append the hashed value of the concatenation between the value and the randomness
            leaves[key] = hash_concat_data_and_known_rand(value[0],value[1])
            
        for key, value in proofs.items():
            res = verify_proof(root, value, leaves[key], indices[key])
            if not res:
                return False
            
        return True

    def receive_clear_fields(self,policy,clear_fields, proofs, indices):
        # verify if the keys of clear fields and the policy are the same
        return self.__validate_clear_fields(policy,clear_fields, proofs, indices)
        
    # GAME
        
    def receive_commitment(self, params, commitment, signature):
        """ 
        The sala bingo receives the commitment, the signature and the 
        additional parameters from the user. It verifies the signature
        of the user on the commitment and the additional parameters.
        If it is valid, it computes its signature on all of them and 
        returns it to the user.
        # Arguments
            params: list
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
        concat = ""
        for param in params:
            concat += param
        concat += commitment
        # verify the signature of the user on the commitment and the additional parameters
        # using the PK contained in the GP certificate
        extract_public_key(self.GPs[0], "Bingo/GP_PK.pem")
        with open("Bingo/concat.txt", "w") as f:
            f.write(concat)
        if verify_ECDSA("Bingo/GP_PK.pem", "Bingo/concat.txt", signature):
            # compute the signature of the sala bingo on all of them
            sign_ECDSA(self.SK, "Bingo/concat.txt", "Bingo/signature.pem")
            return "Bingo/signature.pem"
        return None
            
    
    def publish_commitments_and_signature(self):
        """ 
        Once it has received all the commitments, the sala bingo publishes
        them and its signature on them.
        
        # Returns
            commitments: list
                The list of commitments.
            signature: string
                The signature of the sala bingo on the commitments.
        """
        pass
    
    def receive_opening(self, opening):
        """ 
        The sala bingo receives the opening from the user.
        """
        pass

    def publish_openings(self):
        """ 
        Once received all the openings, the sala bingo computes the
        final string and publishes the openings as (message, randomness) 
        pairs.
        # Returns
            openings: list
                The list of openings.
        """
        pass