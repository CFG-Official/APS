from player import Player
from bingo import Bingo
from AS import AS
from DPA import DPA
import AS_authentication as AS_util
import bingo_authentication as bingo_util
import round
import time
import os

performance = {}

def main():
    # A user requires a GP to play
    folder = "Application"
    if os.path.exists(folder):
        os.system("rm -r " + folder)
    os.mkdir(folder)
    
    alice = Player(["Alice", "IT", "F", "Rome", "1990-01-01", "CF1"], folder)
    bob = Player(["Bob", "IT", "F", "Rome", "1999-01-01", "CF2"], folder)

    print("---------- GP REQUEST ----------")
    print("-> ", alice.get_name(), "Requires the GP to the AS...")
    print("-> ", bob.get_name(), "Requires the GP to the AS...")
    start_time = time.time()
    authority = AS(folder)
    AS_util.authentication(alice, authority)
    performance["Alice Authentication"] = time.time() - start_time
    start_time = time.time()
    AS_util.authentication(bob, authority)
    performance["Bob Authentication"] = time.time() - start_time

    # The user now owns a GP and wants to authenticate to the sala bingo
    print("---------- Bingo AUTHENTICATION ----------")
    #bingo = EvilBingo()
    start_time = time.time()
    bingo = Bingo(folder)
    bingo.set_blockchain()
    alice.set_auth_id(bingo_util.authentication(alice,bingo))
    bob.set_auth_id(bingo_util.authentication(bob,bingo))
    performance["Bingo Authentication"] = time.time() - start_time
    print("---------- Bingo VALIDATION ----------")
    policy = DPA().choose_policy()
    start_time = time.time()
    res_validation_alice = bingo_util.validation(alice,bingo,policy)
    res_validation_bob = bingo_util.validation(bob,bingo,policy)

    if res_validation_alice is None:
        print("Player Alice is not allowed to play")
    if res_validation_bob is None:
        print("Player Bob is not allowed to play")
    performance["Bingo Validation"] = time.time() - start_time    
    game_code = res_validation_alice[0]
    alice_id = res_validation_alice[1]
    bob_id = res_validation_bob[1]

    # The user is now authenticated and can play
    print("---------- GAME STARTING ----------")
    start_time = time.time()
    bingo.start_game()
    alice.start_game(game_code,alice_id, res_validation_alice[2])
    bob.start_game(game_code,bob_id, res_validation_bob[2])
    
    bingo.receive_mapping(alice_id, alice.generate_mapping()) # Receive the mapping from the player
    bingo.receive_mapping(bob_id, bob.generate_mapping()) # Receive the mapping from the player
    
    bingo.add_pre_game_block()
    performance["Players initializations"] = time.time() - start_time
    start_time = time.time()
    round.multi_play([alice,bob],bingo)
    performance["One Round Time"] = time.time() - start_time
    start_time = time.time()
    winner = bingo.choose_winner()
    
    signs = []
    signs.append(bob.get_winner(winner))
    signs.append(alice.get_winner(winner))

    bingo.end_game(signs)
    
    bob.end_game()
    alice.end_game()
    performance["Winner proclamation and end game"] = time.time() - start_time

    print("---------- GAME END ----------")
    print("---------- PERFORMANCE ----------")
    for key in performance:
        print(key, ":", performance[key])

if __name__ == "__main__":
    main()