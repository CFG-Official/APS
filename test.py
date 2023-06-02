import utils.keys_util as KU
import utils.certificates_util as CU
import utils.CA_util as CAU
import utils.pseudorandom_util as PRG
import utils.hash_util as HU

# set the test variable
test = "rand"

# WARNING: clean the test folders before doing any test !!!

if test == "ECDSAkeys":
    
    print("Testing keys")
    # Test ECDSA keys generation
    folder = "tests/keys/"
    KU.gen_ECDSA_keys("prime256v1", folder+"param.pem", folder+"privKey.pem", folder+"pubKey.pem")

    # Test ECDSA keys viewing
    print(KU.view_ECDSA_params(folder+"param.pem"))
    print(KU.view_ECDSA_priv_key(folder+"privKey.pem"))
    print(KU.view_ECDSA_pub_key(folder+"pubKey.pem"))
    
elif test == "RSAkeys":
    
    print("Testing keys")
    # Test RSA keys generation
    folder = "tests/keys/"
    KU.gen_RSA_keys(2048, folder+"privKey.pem")
    KU.export_RSA_pub_key(folder+"privKey.pem", folder+"pubKey.pem")
    print(KU.view_RSA_priv_key(folder+"privKey.pem"))
    print(KU.view_RSA_pub_key(folder+"pubKey.pem"))
    
elif test == "RSAsign":
    
    print("Testing signing")
    # Test RSA signing
    folder = "tests/keys/"
    KU.sign_RSA(folder+"privKey.pem", "tests/test.txt", folder+"sign.txt")
    print(KU.verify_RSA(folder+"pubKey.pem", "tests/test.txt", folder+"sign.txt"))
    
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
    CU.auto_sign_certificate(365, "tests/keys/privKey.pem", folder+"autoCert.cert", "configuration_files/testCA_config.cnf")
    # View certificate
    print(CU.view_auto_certificate(folder+"autoCert.cert"))
    
elif test == "CA":
    
    # Requires CA cert and key generation
    folder = "tests/CA/"
    # Create CA
    CAU.create_CA(folder+"testCA", "tests/keys/privKey.pem", "tests/keys/pubKey.pem", folder+"testCA.cert", "prime256v1", "tests/keys/param.pem", 365, "configuration_files/base_config.cnf")
    #CAU.sign_cert("tests/certificates/csr.pem", folder+"autoCert.cert", "configuration_files/testCA_config.cnf")
    CAU.sign_cert_with_extension("tests/certificates/csr.pem", folder+"autoCert.cert", "configuration_files/testCA_config.cnf", "configuration_files/extensions.cnf")
    
elif test == "rand":
    PRG.pseudo_random_gen("palle.hex",24,"base64")
    print(PRG.pseudo_random_view("palle.hex","base64"))
    
elif test == "hash":
    
    HU.compute_hash_from_file("tests/randomness/randomness.bin", "tests/hash/randomness", "sha3-256")
    
else:
    
    print("Invalid test. Clean the test folders before doing any test, then choose the test!")
    