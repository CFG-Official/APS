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