from models.cb.rounds import Round


class Queue:
    def __init__(self):
        self.rounds = [Round() for _ in range(3)]
        self.currentRound = 1
        self.currentBoss = 1
        self.currentTier = 1


    def updateTier(self):
        if int(self.currentRound) >= 45:
            self.currentTier = 5
        elif int(self.currentRound) >= 35:
            self.currentTier = 4
        elif int(self.currentRound) >= 11:
            self.currentTier = 3
        elif int(self.currentRound) >= 4:
            self.currentTier = 2
        else:
            self.currentTier = 1
