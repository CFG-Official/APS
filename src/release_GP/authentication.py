from user import User
from AS import AS

if __name__ == "__main__":
    # Create the user and the AS
    alice = User("Alice")
    authority = AS()
    # The AS sends a random string to the user
    rand = authority.send_randomness()
    # The user sends the CIE certificate and the signature of the concatenation between the cerificate and the random string to the AS
    cert, signature = alice.send_CIE_and_sign(rand)
    # The AS verifies the signature of the user
    authority.verify_signature(cert, signature)
    
    






