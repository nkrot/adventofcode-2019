
class PlayerFollower(object):
    """
    Player that implements simple playing strategy:
    - before the first contact of the paddle and the ball -- wait
    - after that, follow the ball with the paddle
    """

    def __init__(self, game=None):
        self.game = game
        self.outputs = []
        self.ball = None
        self.after_first_bounce = False
    
    def execute(self):
        if self._ball_moved():
            self._play()

    def _ball_moved(self):
        return not self.ball == self.game.ball

    def _play(self):
        cmd = 0

        if not self.after_first_bounce and self.ball:
            self.after_first_bounce = self.game.ball[0] < self.ball[0]

        if self.after_first_bounce:
            dh = self.game.ball[1] - self.ball[1]
            if   dh > 0: cmd = 1
            elif dh < 0: cmd = -1
            else:        cmd = 0

        self.ball = self.game.ball
        self.outputs.append(cmd)
