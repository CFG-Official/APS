from user import User
from AS import AS

if __name__ == "__main__":
    # Create the user and the AS
    # CIE = [name and surname, nation (2 letters), gender, birthplace, birthday, CF]
    alice = User(["Alice", "IT", "F", "Rome", "1990-01-01", "CF"])
    authority = AS()
    # The AS sends a random string to the user
    rand = authority.send_randomness()
    # The user sends the CIE certificate and the signature of the concatenation between the cerificate and the random string to the AS
    cert, signature = alice.send_CIE_and_sign(rand)
    # The AS verifies the signature of the user
    authority.verify_signature(cert, signature)
    
    # The user sends the CSR to the AS
    GP_csr = alice.require_GP()
    # The AS signs the CSR and sends the certificate to the user along with the clear fields
    cert, clear_fields = authority.release_GP(GP_csr) 
    # make interactive if needed <-- TODO
    alice.get_GP(cert, clear_fields)
    
    
    






