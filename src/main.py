import sys
from player import Player
from bingo import Bingo
from DPA import DPA
from AS import AS
from blockchain import Blockchain

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
    bingo.set_blockchain()
    game_code, player_id = bingo_util.authentication(alice,bingo)
    bingo.add_pre_game_block()
    # The user is now authenticated and can play
    print("---------- GAME STARTING ----------")
    print("Game starting...")
    alice.start_game(game_code,player_id)
    round.play(alice, bingo)
    alice.end_game()

if __name__ == "__main__":
    main()