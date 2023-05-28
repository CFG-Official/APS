import Utils.BashUtil as BU
from Utils.Commands import commands

@staticmethod
def genECDSAkeys(curveName, paramFile, privKeyFile, pubKeyFile):
    """
    Generates ECDSA keys using the openssl bash command.
    # Arguments
        curveName: The name of the curve to use.
        paramFile: The file to store the parameters in.
        privKeyFile: The file to store the private key in.
        pubKeyFile: The file to store the public key in.
    """ 
    BU.executeCommand(commands["ECDSAparamsGen"](curveName, paramFile))
    BU.executeCommand(commands["ECDSAprivKeyGen"](paramFile, privKeyFile))
    BU.executeCommand(commands["ECDSApubKeyGen"](privKeyFile, pubKeyFile))
    
@staticmethod
def viewECDSAparams(paramFile):
    """
    Views ECDSA parameters using the openssl bash command.
    # Arguments
        paramFile: The file to read the parameters from.
    # Returns
        The output of the command.
    """ 
    return BU.executeCommand(commands["ECDSAparamsView"](paramFile))
    
@staticmethod
def viewECDSAprivKey(privKeyFile):
    """
    Views ECDSA private key using the openssl bash command.
    # Arguments
        privKeyFile: The file to read the private key from.
    # Returns
        The output of the command.
    """ 
    return BU.executeCommand(commands["ECDSAprivKeyView"](privKeyFile))
    
@staticmethod
def viewECDSApubKey(pubKeyFile):
    """
    Views ECDSA public key using the openssl bash command.
    # Arguments
        pubKeyFile: The file to read the public key from.
    # Returns
        The output of the command.
    """ 
    return BU.executeCommand(commands["ECDSApubKeyView"](pubKeyFile))

