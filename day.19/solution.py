#!/usr/bin/env python

# # #
#
#

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from aoc.intcode import Tape, Interpreter

class Scanner(object):
    def __init__(self, tape=None):
        self.tape = tape
        self.verbose = False

    def execute(self, board):
        self.board = board
        print(f'scanning the board of (height,width)={self.board.shape}')

        readings = []

        for y,x in self.positions():
            self._vprint(f"Position: {(x,y)}")
            tape = Tape(self.tape)
            tape.rewind() # TODO: necessary?

            computer = Interpreter(tape, inputs=[x,y], outputs=readings)
            computer.execute()
            state = readings.pop(0)
            if state == 0:
                state = 2
            self.board.mark_as((y,x), state)
            self._vprint(str(self.board))

    def positions(self):
        """
        positions on the board to check
        """
        beam = []
        tip = (-1, -1) # tip of the beam
        while tip[0] < self.board.shape[0]-1:
            del beam[:]
            x, y = tip[0]+1, tip[1]+1

            # check row (to the west)
            for e in range(1, y+1):
                pos = x, y-e
                yield pos
                if self.board.at(pos) == 1:
                    beam.append(pos)
                else:
                    # NOTE: this may be too early
                    break

            # check row (to the east)
            for e in range(y+1):
                pos = x, y+e
                yield pos
                if self.board.at(pos) == 1:
                    beam.append(pos)
                else:
                    # NOTE: this may be too early
                    break

            # decide what will be new tip of the beam
            # print(beam)
            if len(beam) == 0:
                tip = (tip[0]+1, tip[1]+1)
            else:
                tip = max(beam)

    def _vprint(self, msg):
        if self.verbose:
            print(msg)

class Board(object):

    FIGURES = {
        0: '.',  # drone is stationary
        1: '#',  # drone is pulled
        2: '-',  # checked
    }

    def __init__(self, shape):
        """
        shape is a tuple (height, width)
        """
        self.matrix = np.zeros(shape, dtype=np.int8)

    def at(self, pos):
        return self.matrix[pos]

    @property
    def shape(self):
        return self.matrix.shape

    def mark_as(self, pos, val):
        self.matrix[pos] = val

    def visualize(self, compact=True):
        """
        Generate a string representing the board in human-readable format.
        """
        sep = {True: '', False: ' '}[compact]
        lines = []
        for row in self.matrix:
            line = sep.join([self.FIGURES[col] for col in row])
            lines.append(line)
        pic = "\n".join(lines)
        return pic

    def __str__(self):
        return self.visualize()

    def count_points_under_beam(self):
        return self.matrix[self.matrix == 1].sum()

################################################################################

def run_day_19_1():
    tape = Tape.read_from_file('input.txt')
    expected = 229

    scanner = Scanner(tape)
    scanner.verbose = True
    board = Board((50,50))
    scanner.execute(board)

    print(board)

    res = board.count_points_under_beam()
    print(f"Number of points affected by the tractor beam: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_day_19_2():
    tape = Tape.read_from_file('input.txt')
    expected = -1

    scanner = Scanner(tape)
    board = Board((100,100))
    scanner.execute(board)

    print(board)

if __name__ == '__main__':
    run_day_19_1()
    #run_day_19_2()
