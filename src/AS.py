import datetime
from utils.CA_util import create_CA, sign_cert_with_extension
from utils.keys_util import verify_RSA
from utils.pseudorandom_util import rand_extract, hash_concat_data_and_rand
from utils.certificates_util import concat_cert_and_rand, extract_public_key
from utils.commands_util import commands
from utils.bash_util import execute_command
from utils.hash_util import compute_hash_from_file
from merkle import merkle_tree
from dateutil.relativedelta import relativedelta
import random

class AS:
    """
    This class represents the AS.
    # Attributes
        _AS_auto_certificate: string
            The name of the AS certificate file.
        _PK: string
            The name of the AS public key file.
        _SK: string
            The name of the AS private key file.
        _rand: string
            The random string.
        _security_param: int
            The security parameter.
        _PK_user: string
            The name of the user public key file.
        _CIE_certificate: string
            The name of the CIE certificate file.
        _user_data: string  
            The user data.
    # Methods
        __create_CA()
            Create the CA.
        send_randomness()
            The AS sends a random string to the user.
        __obtain_CIE_PK(CIE_certificate)
            Extract the public key from the CIE certificate.
        __generate_user_data(CIE_certificate)
            Generate the user data.
        verify_signature(CIE_certificate, signature)
            Verify the signature of the CIE certificate.
        __compose_merkle_tree(CIE_certificate)
            Compose the merkle tree.
        release_GP(csr)
            Release the GP certificate.
    """
    
    __slots__ = ['_AS_auto_certificate', '_PK', '_SK', '_rand', '_security_param', '_PK_user', '_CIE_certificate', '_user_data']
    
    def __init__(self):
        self.__create_CA()
        self._security_param = 32 # (in bytes) -> 256 bits
        
    def __create_CA(self):
        """
        Create the CA.
        """
        create_CA("AS", "private_key.pem", "public_key.pem", "auto_certificate.cert", "src/configuration_files/AS.cnf")
        self._AS_auto_certificate = "AS/auto_certificate.cert"
        self._PK = "AS/public_key.pem"
        self._SK = "AS/private/private_key.pem"
        
    def send_randomness(self):
        """
        The AS sends a random string to the user.
        # Returns
            rand: string
                The random string.
        """
        self._rand = rand_extract(self._security_param, "base64")
        print("-> AS: Sent randomness.")
        return self._rand

    def __obtain_CIE_PK(self, CIE_certificate):
        """ 
        Extract the public key from the CIE certificate.
        # Arguments
            CIE_certificate: string
                The name of the CIE certificate file.
        """
        extract_public_key(CIE_certificate, "AS/CIE_PK.pem")
        self._PK_user = "AS/CIE_PK.pem"
        self._CIE_certificate = CIE_certificate
    
    def __generate_user_data(self, CIE_certificate):
        """
        Generate the user data.
        Suppose the CIE to be composed as follows:
        CIE = [name and surname, nation (2 letters), gender, birthplace, birthday, CF]
        Name and birthday will be a datablock of the merkle tree, furthermore we have
        to consider the additional fields contained in the GP certificate:
        - vaccination date,
        - vaccination type.
        # Arguments
            CIE_certificate: string
                The name of the CIE certificate file.
        """
        
        subject = execute_command(commands["cert_extract_subject_fields"](CIE_certificate))
        
        pairs = []
        subject = subject.split(', ')
        for field in subject:
            field = field.split('=')[1].replace("\n","").replace(" ","")
            pairs.append(field)

        self._user_data = {
            "Nome": pairs[4], 
            "Data di nascita": pairs[2],
            "Tipo di vaccino": "Pfizer",
            "Data di vaccinazione": str(datetime.date.today() - relativedelta(months=random.randint(1,7))),
        }
    
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
        body = concat_cert_and_rand(CIE_certificate,self._rand)
        compute_hash_from_file(body, 'AS/hashed_concat.cert')
        if verify_RSA(self._PK_user, 'AS/hashed_concat.cert', signature):
            print("-> AS: CIE signature verified, the user is authentic.")
        else:
            raise Exception("! AS: CIE signature not verified, the user is not authentic.")
        
    def __compose_merkle_tree(self, CIE_certificate):
        """ 
        Compose the merkle tree with the user data.
        # Arguments
            CIE_certificate: string
                The name of the CIE certificate file.
        # Returns
            pairs: dict
                The dict of (data, rand) tuples.
            root: string
                The root of the merkle tree.
        """
        
        self.__generate_user_data(CIE_certificate)
        
        hashed_fields = []
        pairs = {} # dict of (data, rand) tuples
        for name, field in self._user_data.items():
            # hash the data concatenated with the random string
            data, rand, value = hash_concat_data_and_rand(self._security_param,field)
            pairs[name] = (data, rand)
            hashed_fields.append(value)
            
        # compose the merkle tree with the user data
        return pairs, merkle_tree(hashed_fields)
        
    def release_GP(self,csr):
        """ 
        Release the GP.
        # Arguments
            csr: string
                The name of the CSR file.
        # Returns
            cert: string
                The name of the certificate file.
            clear_fields: string
                The clear fields + randomness pairs.
        """
        name = csr.split('_')[0]
        pairs, root = self.__compose_merkle_tree(self._CIE_certificate)
        
        ext = "subjectAltName=DNS:"+root.replace("\n","")

        # create file with extensions
        with open("src/configuration_files/AS_extensions.cnf", "w") as f:
            f.write(ext)
        
        sign_cert_with_extension(csr, name+"_GP.cert", "src/configuration_files/AS.cnf", "src/configuration_files/AS_extensions.cnf")
        
        return name+"_GP.cert", pairs

    