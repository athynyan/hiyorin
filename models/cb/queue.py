from models.cb.rounds import Round


class Queue:
    def __init__(self):
        self.rounds = [Round() for _ in range(3)]
        self.currentRound = None
        self.currentBoss = None
        self.currentTier = None
