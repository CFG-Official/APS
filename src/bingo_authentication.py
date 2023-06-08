from player import Player
from bingo import Bingo

from AS import AS

from AS_authentication import authentication

if __name__ == "__main__":
    # authentication with the AS to get the GP
    alice = Player(["Alice", "IT", "F", "Rome", "1990-01-01", "CF"])
    authority = AS()
    authentication(alice, authority)
    # the user now owns a GP and wants to authenticate to the sala bingo
    bingo = Bingo()
    # the user sends the GP to the sala bingo
    res = bingo.receive_GP(alice.send_GP()) # sala bingo checks if the CA exists and is trusted, the sign is valid and the GP is valid
    print(res)
    # validate GP fields
    
    
    
    
    