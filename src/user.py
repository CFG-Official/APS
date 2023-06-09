from utils.bash_util import execute_command
from utils.keys_util import gen_RSA_keys, export_RSA_pub_key, sign_RSA
from utils.CA_util import create_CA, sign_cert
from utils.commands_util import commands
from utils.certificates_util import require_certificate_with_given_fields, concat_cert_and_rand
from utils.hash_util import compute_hash_from_file

class User:
    """
    This class represents a user.
    # Attributes
        _user_name: string
            The name of the user.
        _CIE_fields: list
            The list of the CIE fields.
        _PK: string
            The name of the user public key file.
        _SK: string
            The name of the user private key file.
        _CIE_certificate: string
            The name of the CIE certificate file.
        _GP_certificate: string
            The name of the GP certificate file.
        _clear_fields: list
            The list of the clear fields.
    # Methods
        __obtain_CIE_keys()
            Obtain the CIE keys.
        __obtain_CIE_certificate()
            Obtain the CIE certificate from the CIE card.
        send_CIE_and_sign(rand)
            Send the CIE certificate and sign the random number contactenated to the certificate.
        require_GP()
            Require the GP certificate.
        get_GP()
            Get the GP certificate.
    """
    
    #__slots__ = ['_user_name', '_CIE_fields', '_PK', '_SK', '_CIE_certificate', '_GP_certificate', '_clear_fields']
    
    def __init__(self,CIE_fields):
        """ 
        Initialize the user.
        """
        self._user_name = CIE_fields[0]
        self._CIE_fields = CIE_fields
        execute_command(commands["create_directory"](self._user_name))  
        self.__obtain_CIE_keys()
        self.__obtain_CIE_certificate()
        self._GP_certificate = None
        self._clear_fields = None

    def __obtain_CIE_keys(self):
        """
        Obtain the CIE keys.
        """
        gen_RSA_keys(2048, self._user_name + "/private_key.pem")
        export_RSA_pub_key(self._user_name + "/private_key.pem", self._user_name + "/public_key.pem")
        self._PK = self._user_name + "/public_key.pem"
        self._SK = self._user_name + "/private_key.pem"

    def __obtain_CIE_certificate(self):
        """
        Obtain the CIE certificate from the CIE card.
        """
        create_CA("MdI", "private_key.pem", "public_key.pem", "auto_certificate.cert", "src/configuration_files/MdI.cnf")
        require_certificate_with_given_fields(self._CIE_fields, self._SK, self._user_name+'/'+self._user_name+"_CIE_request.cert", "src/configuration_files/user.cnf")
        sign_cert(self._user_name+'/'+self._user_name+"_CIE_request.cert", self._user_name+'/'+self._user_name+"_CIE_certificate.cert", "src/configuration_files/MdI.cnf")
        self._CIE_certificate =self._user_name+'/'+self._user_name+"_CIE_certificate.cert"
        
    def send_CIE_and_sign(self,rand):
        """
        Send the CIE certificate and sign the random number contactenated to the certificate.
        # Arguments
            rand: string
                The random number.
        # Returns
            CIE_certificate: string
                The name of the CIE certificate file.
            CIE_signature: string
                The name of the CIE signature file.
        """
        body = concat_cert_and_rand(self._CIE_certificate,rand)
        compute_hash_from_file(body, self._user_name+'/'+self._user_name+"_hashed_concat.cert")
        sign_RSA(self._SK, self._user_name+'/'+self._user_name+"_hashed_concat.cert", self._user_name+'/'+self._user_name+"_CIE_signature.pem")
        print("-> "+self._user_name,": CIE and signature sent")
        return self._CIE_certificate, self._user_name+'/'+self._user_name+"_CIE_signature.pem"
    
    def require_GP(self):
        """
        Compose the csr request for the GP.
        # Returns
            GP_csr: string
                The name of the GP csr file.
        """
        GP_fields = ["--"]*6
        require_certificate_with_given_fields(GP_fields,self._SK, self._user_name+'/'+self._user_name+"_GP_request.csr", "src/configuration_files/user.cnf")
        print("-> "+self._user_name,": CSR request for GP created")
        return self._user_name+'/'+self._user_name+"_GP_request.csr"

    def get_GP(self, GP_certificate, clear_fields):
        """
        Get the GP certificate and the clear fields.
        # Arguments
            GP_certificate: string  
                The name of the GP certificate file.
            clear_fields: string
                The clear fields. 
        """
        self._GP_certificate = GP_certificate
        self._clear_fields = clear_fields