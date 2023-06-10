import random
from dateutil.relativedelta import relativedelta
import datetime

def compare_birthday(value, constraint):
    value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
    return value <= constraint

def compare_vaccination_day(value, constraint):
    value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
    return value >= constraint

def compare_vaccine(value, constraint):
    return value in constraint

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
        num_fields = 4 #random.randint(1, len(self.available_fields))
        self.policy = random.choices(self.available_fields, k=num_fields)
        # remove duplicates
        self.policy = dict.fromkeys(self.policy)
        self.__get_constraints()
        return self.policy
    
    def __get_constraints(self):
        """ 
        Gets the constraints for the policy.
        """
        # The constraints is a upper bound for datetime field:
        # ex: constraints = 26/02/2001
        # the user must be born before 26/02/2001

        for field in self.policy.keys():
            if field == "Data di nascita":
                # Today - 18 years
                today = datetime.date.today()
                eighteen_years_ago = today - relativedelta(years=18)
                self.policy[field] =  (eighteen_years_ago, compare_birthday)
            elif field == "Tipo di vaccino":
                self.policy[field] = (["Pfizer", "Moderna"], compare_vaccine)
            elif field == "Data di vaccinazione":
                # Today - 6 months
                today = datetime.date.today()
                six_months_ago = today - relativedelta(months=6)
                self.policy[field] = (six_months_ago, compare_vaccination_day)
