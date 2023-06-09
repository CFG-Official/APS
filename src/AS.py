import sys, os, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..')) 

from utils.CA_util import create_CA, sign_cert_with_extension
from utils.keys_util import verify_RSA
from utils.pseudorandom_util import rand_extract, hash_concat_data_and_rand
from utils.certificates_util import concat_cert_and_rand
from utils.commands_util import commands
from utils.bash_util import execute_command
from utils.hash_util import compute_hash_from_file
from merkle import merkle_tree

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
        PK_user: string
            The name of the user public key file.
        rand: string
            The random string used for to mark the interaction with the user.
    # Methods
        send_randomness()
            The AS sends a random string to the user.
        obtain_CIE_PK(CIE_certificate)
            Obtain the CIE public key.
        verify_signature(CIE_certificate, signature)
            Verify the signature of the user.
        release_GP_certificate()
            Release the GP certificate.
    """
    
    def __init__(self):
        self.__create_CA()
        self.security_param = 32 # (in bytes) -> 256 bits
        
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
        self.rand = rand_extract(self.security_param, "base64")
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
        self.CIE_certificate = CIE_certificate
    
    def __generate_user_data(self, CIE_certificate):
        """
        Generate the user data.
        Suppose the CIE to be composed as follows:
        CIE = [name and surname, nation (2 letters), gender, birthplace, birthday, CF]
        Name and birthday will be a datablock of the merkle tree, furthermore we have
        to consider the additional fields contained in the GP certificate:
        - vaccination date,
        - vaccination type.
        """
        
        subject = execute_command(commands["cert_extract_subject_fields"](CIE_certificate))
        
        pairs = []
        subject = subject.split(', ')
        for field in subject:
            field = field.split('=')[1].replace("\n","").replace(" ","")
            pairs.append(field)

        self.user_data = {
            "Nome": pairs[4], 
            "Data di nascita": pairs[2],
            "Tipo di vaccino": "Pfizer",
            "Data di vaccinazione": str(datetime.date.today()),
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
        body = concat_cert_and_rand(CIE_certificate,self.rand)
        compute_hash_from_file(body, 'AS/hashed_concat.cert')
        print(verify_RSA(self.PK_user, 'AS/hashed_concat.cert', signature))
        
    def __compose_merkle_tree(self, CIE_certificate):
        """ 
        Compose the merkle tree.
        # Arguments
            CIE_certificate: string
                The name of the CIE certificate file.
        # Returns
            pairs: dict
                The dictionary of the pairs (value, rand) used to compose the merkle tree.
                
            The root of the merkle tree.
        """
        
        self.__generate_user_data(CIE_certificate)
        
        hashed_fields = []
        pairs = {} # dict of (data, rand) tuples
        for name, field in self.user_data.items():
            # hash the data concatenated with the random string
            data, rand, value = hash_concat_data_and_rand(self.security_param,field)
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
        pairs, root = self.__compose_merkle_tree(self.CIE_certificate)
        
        ext = "subjectAltName=DNS:"+root

        # create file with extensions
        with open("src/configuration_files/AS_extensions.cnf", "w") as f:
            f.write(ext)
        
        sign_cert_with_extension(csr, name+"_GP.cert", "src/configuration_files/AS.cnf", "src/configuration_files/AS_extensions.cnf")
        return name+"_GP.cert", pairs

    