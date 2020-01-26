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
        print(f'scanning the board of (height,width)={board.shape}')

        readings = []

        for y,x in board.positions():
            self._vprint(f"Position: {(x,y)}")
            tape = Tape(self.tape)
            tape.rewind() # TODO: necessary?

            computer = Interpreter(tape, inputs=[x,y], outputs=readings)
            computer.execute()
            board.mark_as((y,x), readings.pop(0))
            self._vprint(str(board))

    def _vprint(self, msg):
        if self.verbose:
            print(msg)

class Board(object):

    FIGURES = {
        0: '.', # drone is stationary
        1: '#'  # drone is pulled
    }

    def __init__(self, shape):
        """
        shape is a tuple (height, width)
        """
        self.matrix = np.zeros(shape, dtype=np.int8)

    @property
    def shape(self):
        return self.matrix.shape

    def positions(self):
        """
        Iterate over all cells on the board
        """
        height, width = self.matrix.shape
        for x in range(height):
            for y in range(width):
                yield (x,y)

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
        return self.matrix.sum()

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
