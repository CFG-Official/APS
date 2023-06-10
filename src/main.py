import sys
from player import Player
from bingo import Bingo
from DPA import DPA
from AS import AS

import AS_authentication as AS_util
import bingo_authentication as bingo_util
import round

def main():
    # A user requires a GP to play
    alice = Player(["Alice", "IT", "F", "Rome", "1990-01-01", "CF"])
    print("---------- GP REQUEST ----------")
    print("-> ", alice.get_name(), "Requires the GP to the AS...")
    authority = AS()
    AS_util.authentication(alice, authority)
    # The user now owns a GP and wants to authenticate to the sala bingo
    print("---------- Bingo AUTHENTICATION ----------")
    bingo = Bingo()
    bingo_util.authentication(alice,bingo)
    # The user is now authenticated and can play
    print("---------- GAME STARTING ----------")
    round.play(alice, bingo)

if __name__ == "__main__":
    main()