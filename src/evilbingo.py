from bingo import Bingo

class EvilBingo(Bingo):

    def publish_openings(self):
        """
        Sala bingo after computing the openings, doesn't publish them
        because it's malicious.
        """

        return None