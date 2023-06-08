import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from utils.CA_util import create_CA
from utils.keys_util import verify_RSA
from utils.pseudorandom_util import rand_extract
from utils.certificates_util import concat_cert_and_rand
from utils.commands_util import commands
from utils.bash_util import execute_command
from utils.hash_util import compute_hash_from_file


class AS:
    """
    This class represents the AS.
    # Attributes
        AS_auto_certificate: string
            The name of the AS certificate file.
        PK: string
            The name of the public key file.
        SK: string
            The name of the private key file.
    # Methods
        send_randomness()
            The AS sends a random string to the user.
        obtain_CIE_PK(CIE_certificate)
            Obtain the CIE public key.
        verify_signature(CIE_certificate, signature)
            Verify the signature of the user.
    """
    
    def __init__(self):
        self.__create_CA()
        
    def __create_CA(self):
        """
        Create the CA.
        """
        create_CA("AS", "private_key.pem", "public_key.pem", "auto_certificate.cert", "src/configuration_files/AS.cnf")
        self.AS_auto_certificate = "AS/auto_certificate.cert"
        self.PK = "AS/public_key.pem"
        self.SK = "AS/private/private_key.pem"
        
    def send_randomness(self):
        """
        The AS sends a random string to the user.
        # Returns
            rand: string
                The random string.
        """
        self.rand = rand_extract(12, "base64")
        return self.rand

    def __obtain_CIE_PK(self, CIE_certificate):
        """ 
        Extract the public key from the CIE certificate.
        # Arguments
            CIE_certificate: string
                The name of the CIE certificate file.
        # Returns
            CIE_PK: string
                The PK.
        """
        execute_command(commands["cert_extract_public_key"](CIE_certificate, "AS/CIE_PK.pem"))
        self.PK_user = "AS/CIE_PK.pem"
    
    def verify_signature(self, CIE_certificate, signature):
        """
        Verify the signature of the user.
        # Arguments
            CIE_certificate: string
                The name of the CIE certificate file.
            signature: string
                The name of the signature file.
        """
        self.__obtain_CIE_PK(CIE_certificate)
        body = concat_cert_and_rand(CIE_certificate,self.rand)
        compute_hash_from_file(body, 'AS/hashed_concat.cert')
        print(verify_RSA(self.PK_user, 'AS/hashed_concat.cert', signature))
        