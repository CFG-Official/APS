import utils.keys_util as KU
import utils.certificates_util as CU
import utils.CA_util as CAU

# set the test variable
test = "CA"

# WARNING: clean the test folders before doing any test !!!

if test == "keys":
    
    print("Testing keys")
    # Test ECDSA keys generation
    folder = "tests/keys/"
    KU.gen_ECDSA_keys("prime256v1", folder+"param.pem", folder+"privKey.pem", folder+"pubKey.pem")

    # Test ECDSA keys viewing
    print(KU.view_ECDSA_params(folder+"param.pem"))
    print(KU.view_ECDSA_priv_key(folder+"privKey.pem"))
    print(KU.view_ECDSA_pub_key(folder+"pubKey.pem"))
    
elif test == "certs":
    
    # !!! Requires key generation !!!
    
    print("Testing certificates")
    # Test certificate signing request generation
    folder = "tests/certificates/"
    CU.require_certificate("tests/keys/privKey.pem", folder+"csr.pem", "configuration_files/base_config.cnf")
    print(CU.view_certificate(folder+"csr.pem"))
    
    fields = ["Nome: ", "Sesso (2 caratteri): ", "Cognome: ", "Data di nascita (i backslash li ignora): ", "Luogo di nascita: ", "Codice fiscale: "]
    CU.interactive_require_certificate(fields, "tests/keys/privKey.pem", folder+"csr2.pem", "configuration_files/base_config.cnf")
    print(CU.view_certificate(folder+"csr2.pem"))
    
    #Autosign certificate
    CU.auto_sign_certificate(365, "tests/keys/privKey.pem", folder+"autoCert.cert", "configuration_files/base_config.cnf")
    # View certificate
    print(CU.view_auto_certificate(folder+"autoCert.cert"))
    
elif test == "CA":
    
    # Requires CA cert and key generation
    folder = "tests/CA/"
    # Create CA
    CAU.create_CA(folder+"testCA", "tests/keys/privKey.pem", "tests/keys/pubKey.pem", folder+"testCA.cert", "prime256v1", "tests/keys/param.pem", 365, "configuration_files/base_config.cnf")
    
else:
    
    print("Invalid test. Clean the test folders before doing any test, then choose the test!")
    