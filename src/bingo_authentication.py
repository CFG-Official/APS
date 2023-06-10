import sys
from player import Player
from bingo import Bingo
from DPA import DPA
from AS import AS

import AS_authentication as AS_util

def authentication(user, bingo):
    print("-- ESTABILISHED TLS CONNECTION --")
    user.set_PK_bingo(bingo.get_PK())
    # the user sends the GP to the sala bingo
    if bingo.receive_GP(user.send_GP()): 
        # sala bingo checks if the CA exists and is trusted, the sign is valid and the GP is valid
        print("- Valid GP! Starting authentication...")
    else:
        print("- Invalid GP! Terminating...")
        return
    
def validation(user, bingo):
    # DPA chooses the daily policy
    dpa = DPA()
    policy = dpa.choose_policy()
    # validate GP fields according to the daily policy
    clear_fields, merkle_proofs, indices = user.send_clear_fields(policy)
    try:
        game_code, last_id, blocks = bingo.receive_clear_fields(policy, clear_fields, merkle_proofs, indices)
    except:
        print("- Invalid GP! Terminating...")
        return
    return game_code, last_id, blocks
