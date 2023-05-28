import Utils.KeysUtil as KU
import Utils.CertificatesUtil as CU

# set the test variable
test = ""

# WARNING: clean the test folders before doing any test !!!

if test == "keys":
    
    print("Testing keys")
    # Test ECDSA keys generation
    folder = "Tests/Keys/"
    KU.genECDSAkeys("prime256v1", folder+"param.pem", folder+"privKey.pem", folder+"pubKey.pem")

    # Test ECDSA keys viewing
    print(KU.viewECDSAparams(folder+"param.pem"))
    print(KU.viewECDSAprivKey(folder+"privKey.pem"))
    print(KU.viewECDSApubKey(folder+"pubKey.pem"))
    
elif test == "certs":
    
    # !!! Requires key generation !!!
    
    print("Testing certificates")
    # Test certificate signing request generation
    folder = "Tests/Certificates/"
    CU.requireCertificate("Tests/Keys/privKey.pem", folder+"csr.pem", "ConfigurationFiles/baseConfig.cnf")
    print(CU.viewCertificate(folder+"csr.pem"))
    
    fields = ["Nome: ", "Sesso (2 caratteri): ", "Cognome: ", "Data di nascita (i backslash li ignora): ", "Luogo di nascita: ", "Codice fiscale: "]
    CU.interactiveRequireCertificate(fields, "Tests/Keys/privKey.pem", folder+"csr2.pem", "ConfigurationFiles/baseConfig.cnf")
    print(CU.viewCertificate(folder+"csr2.pem"))
    
    #Autosign certificate
    CU.autoSignCertificate(365, "Tests/Keys/privKey.pem", folder+"autoCert.pem", "ConfigurationFiles/baseConfig.cnf")
    # View certificate
    print(CU.viewAutoCertificate(folder+"autoCert.pem"))
    
else:
    
    print("Invalid test. Clean the test folders before doing any test, then choose the test!")
    