# This file contains the Openssl bash commands as strings that will be used in the program.
# The commands are stored in a dictionary with the key being the name of the command and the value being the command itself.
# The commands are stored as strings so that they can be easily executed using the subprocess module.

commands = {
    # ECDSA keys
    "ECDSAparamsGen": lambda name, outFile: f'openssl ecparam -name {name} -out {outFile}',
    "ECDSAparamsView": lambda inFile: f'openssl ecparam -in {inFile} -text',
    "ECDSAprivKeyGen": lambda paramFile, outFile: f'openssl genpkey -paramfile {paramFile} -out {outFile}',
    "ECDSAprivKeyView": lambda inFile: f'openssl pkey -in {inFile} -text',
    "ECDSApubKeyGen": lambda privKeyFile, outFile: f'openssl pkey -in {privKeyFile} -pubout -out {outFile}',
    "ECDSApubKeyView": lambda inFile: f'openssl pkey -pubin -in {inFile} -text',
    # Certificate Signing Requests
    "CSRgen": lambda privKeyFile, outFile, configFile: f'openssl req -new -key {privKeyFile} -out {outFile} -config {configFile}',
    "CSRInteractiveGen": lambda privKey, outFile, configFile, f1, f2, f3, f4, f5, f6: f'openssl req -new -key {privKey} -out {outFile} -config {configFile} -subj "/CN={f1}/C={f2}/ST={f3}/L={f4}/O={f5}/OU={f6}"'
,
    "CSRview": lambda inFile: f'openssl req -in {inFile} -text',
 }
