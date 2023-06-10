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
        sys.exit()
    # DPA chooses the daily policy
    dpa = DPA()
    policy = dpa.choose_policy()
    # validate GP fields according to the daily policy
    clear_fields, merkle_proofs, indices = user.send_clear_fields(policy)
    try:
        game_code, last_id = bingo.receive_clear_fields(policy, clear_fields, merkle_proofs, indices)
    except:
        print("- Invalid GP! Terminating...")
        return
    return game_code, last_id
        

if __name__ == "__main__":
    # authentication with the AS to get the GP
    alice = Player(["Alice", "IT", "F", "Rome", "1990-01-01", "CF"])
    authority = AS()
    AS_util.authentication(alice, authority)
    # the user now owns a GP and wants to authenticate to the sala bingo
    bingo = Bingo()
    authentication(alice,bingo)
    print("Game starting...")
    alice.start_game("0","0")
    # player sends the parameters, commitment and signature to the bingo and 
    # it verifies the signature and, if it is valid, it computes its signature
    # on all of them and returns it to the user
    sign = bingo.receive_commitment(*alice.send_commitment())
    if sign:
        # player verifies the signature of the sala bingo on the commitment and the additional parameters
        # if it is not valid, it aborts the game, otherwise it continues
        if not alice.receive_signature(sign):
            print("Not valid signature! Terminating...")
            sys.exit()
    else:
        print("Not valid signature! Terminating...")
        sys.exit()
    print("- Valid server signature, waiting for the other players...")
    
    if alice.receive_commitments_and_signature(*bingo.publish_commitments_and_signature()):
        # player verifies the signature of the sala bingo on the commitments
        print("- Valid server signature, opening the contribution...")
    else:
        print("Not valid signature! Terminating...")
        sys.exit()
        
    # player sends the opening to the slaa bingo
    bingo.receive_opening(*alice.send_opening())
    
    # bingo verifies the opening and, if the commitments are valid, it computes its signature
    # on the concatenation of all the contributions and returns it to the user along
    # with the openings
    print(alice.receive_openings(*bingo.publish_openings()))
    print("Sono la Sala Bingo e ho ottenuto:", bingo.get_final_string())
    print("Sono il player e ho ottenuto:", alice.get_final_string())

    
    
    


    
    
    
    
    
    
    