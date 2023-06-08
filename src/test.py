import utils.keys_util as KU
import utils.certificates_util as CU
import utils.CA_util as CAU
import utils.pseudorandom_util as PRG
import utils.hash_util as HU

# set the test variable
test = "hash"
folder = "tests/"

# WARNING: clean the test folders before doing any test !!!

if test == "ECDSAkeys":
    
    print("Testing keys")
    # Test ECDSA keys generation
    folder = folder + "/keys/"
    KU.gen_ECDSA_keys("prime256v1", folder+"param.pem", folder+"privKey.pem", folder+"pubKey.pem")

    # Test ECDSA keys viewing
    print(KU.view_ECDSA_params(folder+"param.pem"))
    print(KU.view_ECDSA_priv_key(folder+"privKey.pem"))
    print(KU.view_ECDSA_pub_key(folder+"pubKey.pem"))
    
elif test == "RSAkeys":
    
    print("Testing keys")
    # Test RSA keys generation
    folder = folder + "/keys/"
    KU.gen_RSA_keys(2048, folder+"privKey.pem")
    KU.export_RSA_pub_key(folder+"privKey.pem", folder+"pubKey.pem")
    print(KU.view_RSA_priv_key(folder+"privKey.pem"))
    print(KU.view_RSA_pub_key(folder+"pubKey.pem"))
    
elif test == "RSAsign":
    
    print("Testing signing")
    # Test RSA signing
    folder = folder + "/keys/"
    KU.sign_RSA(folder+"privKey.pem", "tests/test.txt", folder+"sign.txt")
    print(KU.verify_RSA(folder+"pubKey.pem", "tests/test.txt", folder+"sign.txt"))
    
elif test == "certs":
    
    # !!! Requires key generation !!!
    
    print("Testing certificates")
    # Test certificate signing request generation
    folder = folder + "certificates/"
    CU.require_certificate("tests/keys/privKey.pem", folder+"csr.pem", "src/configuration_files/base_config.cnf")
    print(CU.view_certificate(folder+"csr.pem"))
    
    fields = ["Nome: ", "Sesso (2 caratteri): ", "Cognome: ", "Data di nascita (i backslash li ignora): ", "Luogo di nascita: ", "Codice fiscale: "]
    CU.interactive_require_certificate(fields, "tests/keys/privKey.pem", folder+"csr2.pem", "src/configuration_files/base_config.cnf")
    print(CU.view_certificate(folder+"csr2.pem"))
    
    #Autosign certificate
    CU.auto_sign_certificate(365, "tests/keys/privKey.pem", folder+"autoCert.cert", "src/configuration_files/testCA_config.cnf")
    # View certificate
    print(CU.view_auto_certificate(folder+"autoCert.cert"))
    
elif test == "CA":
    
    # Requires CA cert and key generation
    folder = folder + "CA/"
    # Create CA
    CAU.create_CA(folder+"testCA", "tests/keys/privKey.pem", "tests/keys/pubKey.pem", folder+"testCA.cert", "src/configuration_files/base_config.cnf")
    #CAU.sign_cert("tests/certificates/csr.pem", folder+"autoCert.cert", "src/configuration_files/testCA_config.cnf")
    CAU.sign_cert_with_extension("tests/certificates/csr.pem", folder+"autoCert.cert", "src/configuration_files/testCA_config.cnf", "src/configuration_files/extensions.cnf")
    
elif test == "rand":
    
    rand = PRG.rand_extract(1,"base64")
    print(PRG.convert_rand_to_num(rand, "base64"))
    
elif test == "hash":

    rand = PRG.convert_rand_to_num(PRG.rand_extract(1,"base64"), "base64")
    
    print(rand)
    print(HU.compute_hash_from_data(rand))
    
else:
    
    print("Invalid test. Clean the test folders before doing any test, then choose the test!")
    