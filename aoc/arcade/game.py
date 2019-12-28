
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from intcode import Tape, Interpreter

import numpy as np

class Game(object):
    EMPTY  = 0
    WALL   = 1
    BLOCK  = 2
    PADDLE = 3
    BALL   = 4

    def __init__(self, shape, tape=None):
        self.w = shape[0] # width
        self.h = shape[1] # height
        self.board = np.zeros((self.h, self.w), dtype=np.int8) 
        self.verbose = False
        self.score = 0

        self.paddle = None # position of the paddle
        self.ball   = None # position of the ball
        
        if tape:
            self.inputs = []
            self.computer = Interpreter(tape)
            self.computer.set_uplink_to(self)

        self._player = None

        self.figures = {
            self.EMPTY  : '.', # 0 is an empty tile. No game object appears in this tile.
            self.WALL   : 'W', # 1 is a wall tile. Walls are indestructible barriers.
            self.BLOCK  : 'B', # 2 is a block tile. Blocks can be broken by the ball.
            self.PADDLE : '=', # 3 is a horizontal paddle tile. The paddle is indestructible.
            self.BALL   : 'o', # 4 is a ball tile. The ball moves diagonally and bounces off objects.
        }

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, pl):
        self._player = pl
        self._player.game = self
        self.computer.inputs = self._player.outputs

    def execute(self):
        while not self.computer.finished:
            self.computer.execute()
            if len(self.inputs) == 3:
                self._execute()

    def _execute(self):
        """
        Low level method that interprets commands in the input buffer
        """
        arg1 = self.inputs.pop(0)
        arg2 = self.inputs.pop(0)
        arg3 = self.inputs.pop(0)
    
        if arg1 == -1 and arg2 == 0:
            self.score = arg3
        else:
            self.draw(arg1, arg2, arg3)
            if self.player:
                self.player.execute()
    
    def draw(self, x, y, tile):
        """
        x - horizontal offset (distance from the left)
        y - vertical offset (distance from the top)
        """
        #self._vprint(f"Drawing ({x},{y}) as {tile}/{self.figures[tile]}")
        self.board[y,x] = tile

        if tile == self.PADDLE:
            self.paddle = (y,x)

        if tile == self.BALL:
            self.ball = (y,x)

        print(self)

    def __str__(self):
        lines = []
        for row in self.board:
            lines.append("".join([self.figures[c] for c in row]))
        lines.append(f"SCORE: {self.score}; PADDLE: {self.paddle}; BALL: {self.ball}")
        return "\n".join(lines)

    def _vprint(self, msg):
        if self.verbose:
            print(msg)

