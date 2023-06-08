from user import User

class Player(User):
    
    """ 
    This class represents a player of the bingo game, it inherits from the User class.
    """
    
    def send_GP(self):
        return self.GP_certificate