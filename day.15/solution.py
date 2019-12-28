#!/usr/bin/env python

# # #
# TODO: reuse day 11 PaintingRobot or 13 ArcadeGame?
#

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import random

from aoc.intcode import Tape, Interpreter

import numpy as np

################################################################################

class RemoteControl(object):

    # movement instructions to the RepairDroid
    NORTH, SOUTH, WEST, EAST = 1, 2, 3, 4
    MOVEMENTS = [NORTH, SOUTH, WEST, EAST]

    # Status codes received from the RepairDroid, describing what the current position is
    WALL  = 0 # The repair droid hit a wall. Its position has not changed.
    EMPTY = 1 # The repair droid has moved one step in the requested direction.
    GOAL  = 2 # The repair droid has moved one step in the requested direction;
              # its new position is the location of the oxygen system (GOAL).

    def __init__(self, program=None):
        self.computer = None
        self._program = None
        self.inputs = []
        self.outputs = []
        if program is not None:
            self.program = program
        self.verbose = False

    @property
    def movement_commands(self):
        """
        This is just an alias that allows to think in domain terms
        """
        return self.outputs

    @property
    def droid_status_codes(self):
        """
        This is just an alias that allows to think in domain terms
        """
        return self.inputs
    
    @property
    def program(self):
        return self._program

    @program.setter
    def program(self, program):
        if isinstance(program, Tape):
            self._program = program
            # computer is the repair droid
            self.computer = Interpreter(self._program, self.outputs)
            self.computer.set_uplink_to(self)
        else:
            raise ValueError(f"Can not set program from object of type {type(program)}")

    def execute(self):
        self._vprint("RemoteConrol running")

        while not self.computer.finished:
            # repair droid accepts a movement instruction (0-4) and outputs status code (0-3)
            
            self.generate_movement_instruction()
            self.computer.execute()
            self.interpret_status_code()

    def generate_movement_instruction(self):
        """
        Decide where to move and put corresponding code into <movement_commands>.
        """

        cmd = random.choice(self.MOVEMENTS) # TODO: do something smarter
        self.movement_commands.append(cmd)
        
        self._vprint(f"State of movement commands (remote control -> droid): {self.movement_commands}")

    def interpret_status_code(self):
        """
        Interpret the status code from the repair droid
        """
        self._vprint(f"State of status codes (droid -> remote control): {self.droid_status_codes}")
        code = self.droid_status_codes.pop(0)

        pos = (0,0) # TODO: position where we attempted to move
        if code == self.WALL:
            self.board.mark_as(pos, board.WALL)
            # droid did not move
        elif code == self.EMPTY:
            self.board.mark_as(pos, board.OPEN)
            self.board.mark_as(pos, board.PLAYER)
        elif code == self.GOAL:
            self.board.mark_as(pos, board.GOAL)
            # TODO: stop the game
        else:
            raise ValueError(f"Illegal code received from Repair Droid: {code}")

    def _vprint(self, msg):
        if self.verbose:
            print(msg)

class Board(object):

    UNKNOWN = 0  # unopened cell (initial state)
    OPEN    = 1  # pass is possible
    WALL    = 2  # wall hit, pass not possible
    GOAL    = 3  # the cell is the goal
    PLAYER  = 4  # current position of the player

    FIGURES = {
        UNKNOWN: '.',
        OPEN:    '+',
        WALL:    '#',
        GOAL:    'G',
        PLAYER:  'D'
    }

    def __init__(self, shape):
        self.shape = shape
        self.matrix = np.zeros(shape, dtype=np.int8)
        self.player = None # position of the player as tuple (x,y)

    def mark_as(self, pos, code):
        """
        Mark given position <pos> as one of UNKNOWN|OPEN|WALL|GOAL|PLAYER
        """
        if code == self.PLAYER:
            self.player = pos
        else:
            self.matrix[pos] = code
        
    def visualize(self):
        """ 
        Generate a string representing the board in human-readable format.
        """
        lines = []
        for row in self._matrix_with_player:
            line = " ".join([self.FIGURES[c] for c in row])
            lines.append(line)
        pic = "\n".join(lines)
        return pic

    @property
    def _matrix_with_player(self):
        matrix = self.matrix
        if self.player is not None:
            matrix = self.matrix.copy()
            matrix[self.player] = self.PLAYER
        return matrix
    
################################################################################

def run_tests_15_1():
    print("=== Day 15, Task 1 (tests) ===")

    board = Board((10,10))

    board.mark_as((0,0), board.WALL)
    board.mark_as((0,1), board.WALL)
    board.mark_as((0,2), board.WALL)
    
    board.mark_as((1,1), board.OPEN)
    board.mark_as((1,2), board.OPEN)
    board.mark_as((2,2), board.OPEN)

    board.mark_as((2,3), board.GOAL)
    board.mark_as((2,4), board.PLAYER)
        
    print(board.visualize())


def run_day_15_1():
    print("=== Day 15, Task 1 ===")

    verbose = True

    remote = RemoteControl()
    remote.board = Board((10,10))
    print(remote.board.visualize())
    exit(100)

    remote.program = Tape.read_from_file("input.txt")
    remote.verbose = verbose
    # remote.computer.verbose = verbose

    remote.board = Board((10,10))
    
    remote.execute()


def run_tests_15_2():
    
    print("=== Day 15, Task 2 (tests) ===")
    pass


def run_day_15_2():
    print("=== Day 15, Task 2 ===")
    pass

if __name__ == '__main__':
    run_tests_15_1()
    # run_day_15_1()

    # run_tests_15_2()
    # run_day_15_2()

    
