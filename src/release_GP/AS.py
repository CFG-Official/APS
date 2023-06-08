import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from utils.CA_util import create_CA
from utils.pseudorandom_util import rand_extract

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
        """
        return rand_extract(12, "base64")

    def obtain_CIE_PK(self, CIE_certificate):
        pass

    def verify_signature(self, CIE_certificate, signature):
        """
        Verify the signature of the user.
        """
        pass