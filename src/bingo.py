import sys, os, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from utils.bash_util import execute_command
from utils.commands_util import commands
from utils.pseudorandom_util import hash_concat_data_and_known_rand
from merkle import merkle_proof, verify_proof

class Bingo:
    
    """ 
    This class represents the sala bingo.
    """
    
    def __init__(self):
        execute_command(commands["create_directory"]("Bingo"))
        execute_command(commands["copy_cert"]("AS/auto_certificate.cert", "Bingo/AS.cert"))
        self.known_CAs = ["Bingo/AS.cert"]
        self.GPs = []
        
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

    def __validate_clear_fields(self, policy, clear_fields):
        
        # length check
        if len(policy) != len(clear_fields):
            return False
        
        # key check
        for item in policy:
            if item not in clear_fields.keys():
                return False
            
        # value check with merkle proofs
        leaves = []
        for value in clear_fields.values():
            # append the hashed value of the concatenation between the value and the randomness
            leaves.append(hash_concat_data_and_known_rand(value[0],value[1]))
            
        # verify the merkle proofs for each leaf
        for index in range(len(leaves)):
            proof = merkle_proof(leaves, index)
            print("PROOF:",proof)
            res = verify_proof(self.__extract_root(self.GPs[0]), proof, leaves[index], index)
            if not res:
                return False
            
        return True

    def receive_clear_fields(self,policy,clear_fields):
        # verify if the keys of clear fields and the policy are the same
        return self.__validate_clear_fields(policy,clear_fields)
        

    