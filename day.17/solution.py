#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import random

from aoc.intcode import Tape, Interpreter

import numpy as np

class BoardBuilder(object):

    SCAFFOLD = 35
    OPEN     = 46
    
    def __init__(self, tape):
        self.computer = Interpreter(tape)
        self.computer.outputs = []
        self.board = None

    def execute(self):
        rows = []
        row = []

        self.computer.execute()
        for code in self.computer.outputs:
            if chr(code) == '\n':
                if len(row) > 0:
                    rows.append(row)
                row = []
            else:
                row.append(code)
    
        self.board = np.array(rows)
        print(self.visualize())

        intersections = self.find_intersections()
        print(f"--- intersections {len(intersections)} ---")
        print(intersections)
        self.total_alignment = sum([x*y for x,y in intersections])

    def visualize(self, board=None):
        board = board or self.board
        lines = []
        for row in board:
            line = " ".join([chr(c) for c in row])
            lines.append(line)
        return "\n".join(lines)

    def find_intersections(self):
        intersections = []
        for point in zip(*np.where(self.board == self.SCAFFOLD)):
            neighbours = self.neighbours_of(point, lambda val: val == self.SCAFFOLD)
            if len(neighbours) == 4:
                intersections.append(point)
        return intersections

    def neighbours_of(self, pos, cond=None):
        results = []
        offsets = [[0,1], [0,-1], [1, 0], [-1,0]]
        for delta_x,delta_y in offsets:
            new_x = pos[0]+delta_x
            new_y = pos[1]+delta_y
            if 0 <= new_x < self.board.shape[0] and 0 <= new_y < self.board.shape[1]:
                val = self.board[new_x, new_y]
                if cond is not None and not cond(val):
                    continue
                results.append((new_x, new_y, val))
        return results

################################################################################

def run_day_17_1():
    tape = Tape.read_from_file("input.txt")
    expected = 13580

    bb = BoardBuilder(tape)
    bb.execute()

    res = bb.total_alignment
    print(f"Answer: sum of all camera alignment parameters: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

if __name__ == '__main__':
    run_day_17_1()

