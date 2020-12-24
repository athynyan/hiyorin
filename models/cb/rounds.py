from models.cb.boss import Boss


class Round:
    def __init__(self):
        self.bosses = [Boss() for _ in range(5)]
        self.messageId = None
