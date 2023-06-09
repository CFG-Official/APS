import random

class DPA:
    """ 
    This class represents the Data Protection Authority (DPA).
    He has the power of choosing the daily policy for the fields to be
    used to validate the GP.
    """
    def __init__(self):
        self.policy = None
        self.available_fields = ["Nome", "Data di nascita", "Tipo di vaccino", "Data di vaccinazione"]
        
    def choose_policy(self):
        """ 
        Chooses the daily policy random between the available ones.
        # Returns
            policy: list
                The list of the fields to be used to validate the GP.
        """
        num_fields = random.randint(1, len(self.available_fields))
        self.policy = random.choices(self.available_fields, k=num_fields)
        # remove duplicates
        self.policy = list(dict.fromkeys(self.policy))
        return self.policy