import sys, os, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from utils.bash_util import execute_command
from utils.keys_util import verify_ECDSA
from utils.commands_util import commands

class Bingo:
    
    """ 
    This class represents the sala bingo.
    """
    
    def __init__(self):
        self.players = {}
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
        return  self.__check_CA(GP, "Bingo/AS.cert") and  self.__check_expiration(GP) and self.__check_sign(GP, "Bingo/AS.cert")
    
if __name__ == "__main__":
    with open("sign.txt", "r") as f:
        sign = f.read()
        # estract the signature value
        sign = sign.split("Signature Value:")[1]
        sign = sign.replace(":", "").replace(" ", "").replace("\n", "")
        print(sign)
        