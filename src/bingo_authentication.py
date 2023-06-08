from player import Player
from AS import AS

from AS_authentication import authentication

if __name__ == "__main__":
    # authentication with the AS to get the GP
    user = Player(["Alice", "IT", "F", "Rome", "1990-01-01", "CF"])
    authority = AS()
    authentication(user, authority)
    # the user now owns a GP
    