import Utils.BashUtil as BU
from Utils.Commands import commands

@staticmethod
def requireCertificate(privKeyFile, outFile, configFile):
    """
        Generates a certificate signing request.
        # Arguments
            privKeyFile: The file containing the private key.
            outFile: The file to output the certificate signing request to.
            configFile: The file containing the configuration for the certificate signing request.
    """
    BU.executeCommand(commands["CSRgen"](privKeyFile, outFile, configFile))
    
@staticmethod
def interactiveRequireCertificate(fields, privKeyFile, outFile, configFile):
    inputs = []
    for field in fields:
        inputs.append(input(field))
    BU.executeCommand(commands["CSRInteractiveGen"](privKeyFile, outFile, configFile, *inputs))
    
@staticmethod
def viewCertificate(inFile):
    """
        Views a certificate signing request.
        # Arguments
            inFile: The file containing the certificate signing request.
        # Returns
            The output of the command.
    """
    return BU.executeCommand(commands["CSRview"](inFile))