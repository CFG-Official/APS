import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from utils.bash_util import execute_command
from utils.keys_util import gen_RSA_keys, export_RSA_pub_key, sign_RSA
from utils.CA_util import create_CA, sign_cert
from utils.commands_util import commands
from utils.certificates_util import require_certificate

class User:
    """
    This class represents a user.
    # Arguments
        user_name: string
            The name of the user.
    # Attributes
        user_name: string
            The name of the user.
        PK: string
            The name of the public key file.
        SK: string
            The name of the private key file.
        CIE_certificate: string
            The name of the CIE certificate file.
    # Methods
        send_CIE_and_sign(rand)
            Send the CIE certificate and sign the random number contactenated to the certificate.
    """
    
    def __init__(self,user_name):
        self.user_name = user_name
        execute_command(commands["create_directory"](user_name))  
        self.__obtain_CIE_keys()
        self.__obtain_CIE_certificate()

    def __obtain_CIE_keys(self):
        """
        Obtain the CIE keys.
        
        """
        gen_RSA_keys(2048, self.user_name + "/private_key.pem")
        export_RSA_pub_key(self.user_name + "/private_key.pem", self.user_name + "/public_key.pem")
        self.PK = self.user_name + "/public_key.pem"
        self.SK = self.user_name + "/private_key.pem"

    def __obtain_CIE_certificate(self):
        """
        Obtain the CIE certificate from the CIE card.
        """
        create_CA("MdI", "private_key.pem", "public_key.pem", "auto_certificate.cert", "src/configuration_files/MdI.cnf")
        require_certificate(self.SK, self.user_name+'/'+self.user_name+"_CIE_request.cert", "src/configuration_files/user.cnf")
        sign_cert(self.user_name+'/'+self.user_name+"_CIE_request.cert", self.user_name+'/'+self.user_name+"_CIE_certificate.cert", "src/configuration_files/MdI.cnf")
        self.CIE_certificate = self.user_name+"_CIE_certificate.cert"

    def send_CIE_and_sign(self,rand):
        """
        Send the CIE certificate and sign the random number contactenated to the certificate.
        """
        sign_RSA(self.SK, self.CIE_certificate, self.user_name+"CIE_signature.sign")
        return self.CIE_certificate, self.user_name+"CIE_signature.sign"

