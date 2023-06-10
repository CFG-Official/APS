import sys
from player import Player
from bingo import Bingo
from AS import AS

import AS_authentication as AS_util
import bingo_authentication as bingo_util
import round

def main():
    # A user requires a GP to play
    alice = Player(["Alice", "IT", "F", "Rome", "1990-01-01", "CF1"])
    bob = Player(["Bob", "IT", "F", "Rome", "1999-01-01", "CF2"])
    print("---------- GP REQUEST ----------")
    print("-> ", alice.get_name(), "Requires the GP to the AS...")
    print("-> ", bob.get_name(), "Requires the GP to the AS...")
    authority = AS()
    AS_util.authentication(alice, authority)    
    AS_util.authentication(bob, authority)

    # The user now owns a GP and wants to authenticate to the sala bingo
    print("---------- Bingo AUTHENTICATION ----------")
    bingo = Bingo()
    # bingo.set_blockchain()
    alice.set_auth_id(bingo_util.authentication(alice,bingo))
    bob.set_auth_id(bingo_util.authentication(bob,bingo))

    print("---------- Bingo VALIDATION ----------")
    policy = DPA().choose_policy()

    res_validation_alice = bingo_util.validation(alice,bingo,policy)
    res_validation_bob = bingo_util.validation(bob,bingo,policy)
    if res_validation_alice is None:
        print("Player Alice is not allowed to play")
    if res_validation_bob is None:
        print("Player Bob is not allowed to play")
        
    game_code = res_validation_alice[0]
    alice_id = res_validation_alice[1]
    bob_id = res_validation_bob[1]

    # The user is now authenticated and can play
    print("---------- GAME STARTING ----------")
    alice.start_game(game_code,alice_id)
    bob.start_game(game_code,bob_id)
    bingo.receive_mapping(alice_id, alice.generate_mapping()) # Receive the mapping from the player
    bingo.receive_mapping(bob_id, bob.generate_mapping()) # Receive the mapping from the player
    
    # bingo.add_pre_game_block()
    round.multi_play([alice, bob], bingo)

    bob.end_game()
    alice.end_game()

if __name__ == "__main__":
    main()