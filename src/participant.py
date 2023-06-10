from utils.bash_util import execute_command
from utils.commands_util import commands
from utils.hash_util import compute_hash_from_data
from utils.keys_util import concatenate, sign_ECDSA
from src.utils.pseudorandom_util import rand_extract
import datetime

class Participant:
    
    __slots__ = ["_seed", "_IV", "_security_param", "_game_code", "_player_id", "_round", "_last_contribute", "_last_randomess", "_last_message"]
    
    def __init__(self):
        self._seed = None
        self._IV = 0
        self._security_param = 32
        self._game_code = None
        self._player_id = None
        self._round = 0
        self._last_contribute = None
        self._last_randomess = None
        self._last_message = None
    
    def set_game_code(self, game_code):
        """
        Set the game code.
        # Arguments
            game_code: string
                The game code.
        """
        if game_code is None:
            raise Exception("Game code not set.")
                
        self._game_code = game_code

    def set_player_id(self, player_id):
        """
        Set the player id.
        # Arguments
            player_id: string
                The player id.
        """
        if player_id is None:
            raise Exception("Player id not set.")

        self._player_id = player_id

    def generate_message(self, SK, name):
        """
        Generate the message to be sent to the sala bingo in commitment phase.
        # Returns
            message: tuple -> (params: tuple -> (player_id, game_code, round, timestamp),
                                comm: string 
                                signature: string)
                The message to be sent to the sala bingo.
        """
        # If no game is started, no message can be computed
        if self._game_code is None or self._player_id is None:
            raise Exception("Game code or player id not set. This player isn't in a game.")
        
        # Set the 
        self._round += 1 # Go to next round
        params = (self._player_id, self._game_code, str(self._round), str(datetime.datetime.now()))

        # Compute commitment for a certain round
        comm = self.__compute_commitment()

        # Sign the message made by params and commitment
        signature = self.__sign_message(SK, concatenate(*list(params), *comm), name)

        self._last_message = (params, comm, signature)

        return self._last_message

    def __compute_commitment(self):
        """
        Extract randomly a contribution for a round and compute the commitment.
        # Returns
            commitment: string
                The commitment of the contribution.
        """
        # Compute the PRF output
        prf_output = execute_command(commands["get_prf_value"](self._seed, self._IV)).split('= ')[1].strip()
        # Update the IV
        self._IV = (self._IV + 1) % (self._security_param)

        # Divide output in two equal parts: the first is the contribution, the second is the randomness used to commit
        self._last_contribute = prf_output[:len(prf_output)//2]
        self._last_randomess = prf_output[len(prf_output)//2:]

        return compute_hash_from_data(self._last_contribute + self._last_randomess)
    
    def __sign_message(self, SK, message, name):
        """
        Sign a message.
        # Arguments
            message: string
                The message to be signed.
        # Returns
            signature: string
                The signature of the message.   
        """
        if message is None:
            raise Exception("Message is None. Can't sign a None message.")
        
        temp_filename = name+'/'+name+"_temp.txt"
        sign_filename = name+'/'+name+'_comm_sign.pem'

        with open(temp_filename, "w") as f:
            f.write(message)

        # sign the message
        print(SK,'-', temp_filename,'-', sign_filename)
        sign_ECDSA(SK, temp_filename, sign_filename)
        return sign_filename
    
    def start_game(self, game_code, player_id, blocks = False):
        """ 
        Start a game.
        # Arguments
            game_code: string
                The game code.
            player_id: string
                The player id.
        """
        self._blockchain = blocks
        self.set_game_code(game_code)
        self.set_player_id(player_id)
        self._round = 0

        # Inizializzo la PRF per il calcolo dei contributi casuali
        self._IV = int(rand_extract(self._security_param, "hex"), 32) # Cast to a 32-bit integer cause it's used as a counter
        self._seed = rand_extract(self._security_param, "base64")

    def end_game(self):
        """ 
        End a game.
        """
        self._game_code = None
        self._player_id = None
        self._round = 0

        self._IV = None
        self._seed = None