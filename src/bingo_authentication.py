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
    res = bingo.receive_GP(user.send_GP())
    if res is not None:
        # sala bingo checks if the CA exists and is trusted, the sign is valid and the GP is valid
        print("- Valid GP! Starting authentication of user" + str(res) + " ...")
        return res
    else:
        print("- Invalid GP! Terminating...")
        sys.exit()

def validation(user, bingo, policy):
    # validate GP fields according to the daily policy
    clear_fields, merkle_proofs, indices = user.send_clear_fields(policy)
    try:
        game_code, last_id, blockchain = bingo.receive_clear_fields(policy, clear_fields, merkle_proofs, indices, user.get_auth_id())

    except:
        print("- Invalid GP! Terminating...")
        return None
    return game_code, last_id, blockchain
