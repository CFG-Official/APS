from user import User

class Player(User):
    
    """ 
    This class represents a player of the bingo game, it inherits from the User class.
    """
    
    def send_GP(self):
        """ 
        Send the GP certificate to the sala bingo.
        # Returns
            GP_certificate: string
                The name of the GP certificate file.
        """
        return self.GP_certificate
    
    def send_clear_fields(self, policy):
        """ 
        Send the pairs to the sala bingo.
        # Arguments
            policy: string
                The policy to be used.
        # Returns
            pairs: dictionary
                The dictionary of pairs.
        """
        # return the fields values whose key is in the policy
        return {key: self.clear_fields[key] for key in policy}