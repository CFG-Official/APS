def authentication(user, authority):

    # The AS sends a random string to the user
    rand = authority.send_randomness()
    # The user sends the CIE certificate and the signature of the concatenation between the cerificate and the random string to the AS
    cert, signature = user.send_CIE_and_sign(rand)
    # The AS verifies the signature of the user
    authority.verify_signature(cert, signature)
    
    # The user sends the CSR to the AS
    GP_csr = user.require_GP()
    # The AS signs the CSR and sends the certificate to the user along with the clear fields
    cert, clear_fields = authority.release_GP(GP_csr) 
    # make interactive if needed <-- TODO
    user.get_GP(cert, clear_fields)
    

    






