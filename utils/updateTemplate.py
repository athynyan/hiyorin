class queueTemplate:
    def __init__(self, active, date, channel, counter, tier, round, boss, kill):
        self.active = active
        self.date = date
        self.channel = channel
        self.counter = counter
        self.currentTier = tier
        self.currentRound = round
        self.currentBoss = boss
        self.kill = kill

class roundTemplate:
    def __init__(self, messageId):
        self.messageId = messageId
        self.data = None
