#!/usr/bin/env python

# # #
# TODO
# 1. Scanner and Beam use transposed coordinates
#    Scanner: x is horizontal offset, y is vertical offset (as in the task definition)
#    Beam: x is vertical offset (top-to-bottom) and y is horizontal (like in numpy matrix)


import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from collections import defaultdict
from itertools import chain

import numpy as np
from aoc.intcode import Tape, Interpreter

class BaseScanner(object):

    def __init__(self, tape=None):
        self.tape = tape
        self.verbose = False
        self.coord = (-1,-1) # current space coordinate scanner is checking

    def execute(self, beam):
        self.beam = beam
        readings = []

        for self.coord in self.positions():
            if self.finished():
                break

            y,x = self.coord
            self._vprint(f"Position: {(x,y)}")

            tape = Tape(self.tape)
            tape.rewind() # TODO: necessary?

            computer = Interpreter(tape, inputs=[x,y], outputs=readings)
            computer.execute()
            if readings.pop(0) == 1:
                self.beam.add((y,x))

            self._vprint(str(self.beam))

    def finished(self):
        """
        Returns true if scanning can be stopped.
        """
        raise NotImpementedError("Subclass must implement this method")

    def positions(self):
        """
        positions to check
        """
        edge = [] # edge of the beam
        tip  = (-1, -1)

        while True:
            del edge[:]
            x, y = tip[0]+1, tip[1]+1

            # check row (to the west)
            for e in range(1, y+1):
                pos = x, y-e
                yield pos
                if pos in self.beam:
                    edge.append(pos)
                else:
                    # NOTE: this may be too early
                    break

            # check row (to the east)
            for e in range(y+1):
                pos = x, y+e
                yield pos
                if pos in self.beam:
                    edge.append(pos)
                else:
                    # NOTE: this may be too early
                    break

            # decide what will be new tip
            # print(edge)
            if len(edge) == 0:
                tip = (tip[0]+1, tip[1]+1)
            else:
                tip = max(edge)

    def _vprint(self, msg):
        if self.verbose:
            print(msg)

class Scanner1(BaseScanner):
    """
    Scanner for task 1
    """
    def __init__(self, *args):
        super(self.__class__, self).__init__(*args)

    def finished(self):
        """
        In this task we need to scan area of 50x50 only
        """
        return self.coord[0] > 49 or self.coord[1] > 49

class Scanner2(BaseScanner):
    """
    Scanner for task 2
    """

    def __init__(self, *args):
        super(self.__class__, self).__init__(*args)

    def finished(self):
        raise NotImplementedError("TODO: Implement stopping condition")

class Beam(object):
    """class that represents the tractor beam"""

    FIGURES = {
        0: '.',  # drone is stationary
        1: '#',  # drone is pulled
        2: '-',  # checked
    }

    def __init__(self):
        self.points = defaultdict(list)

    def __contains__(self, coord):
        v,h = coord
        row = self.points.get(v, [])
        return h in row

    def add(self, coord):
        """
        Adds given point to beam. A point is given as a tuple:
        (vertical_coordinate, horizontal_coordinate)
        """
        # print(f"adding: {coord}")
        vert, hor = coord
        self.points[vert].append(hor)
        return self

    @property
    def area(self):
        return sum(len(hs) for hs in self.points.values())

    def __str__(self):
        return self.visualize()

    def visualize(self, compact=True):
        sep = {True: '', False: ' '}[compact]
        lines = []
        # get vertical min,max and horizontal min,max
        vs = self._minmax(self.points.keys())
        hs = self._minmax(chain.from_iterable(self.points.values()))
        for v in range(vs[0], 1+vs[1]):
            row = []
            for h in range(hs[0], 1+hs[1]):
                if h in self.points.get(v, []):
                    row.append(self.FIGURES[1])
                else:
                    row.append(self.FIGURES[0])
            lines.append(sep.join(row))
        return "\n".join(lines)

    def _minmax(self, lst):
        items = sorted(lst)
        return items[0], items[-1]

def test_beam():
    beam = Beam()
    points = [(4,5), (5,4), (6,5), (7,7), (7,6), (8,6), (8,7), (12, 10), (12,11)]
    for point in points:
        beam.add(point)
    print("")
    print(beam)
    print(f"Area under the beam: {beam.area}")

################################################################################

def run_day_19_1():
    print("=== Day 19, Task 1 ===")

    tape = Tape.read_from_file('input.txt')
    expected = 229

    scanner = Scanner1(tape)
    scanner.verbose = not True
    beam = Beam()
    scanner.execute(beam)
    print(beam)

    res = beam.area
    print(f"Number of points affected by the tractor beam: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_day_19_2():
    # TODO: for this part we need to implement scanner2.finished()

    print("=== Day 16, Task 2 ===")

    tape = Tape.read_from_file('input.txt')
    expected = -1

    scanner = Scanner2(tape)
    scanner.verbose = True
    beam = Beam()
    scanner.execute(beam)

    print(beam)

    # res = -1
    # if res == expected:
    #     print(f"SUCCESS: Got {res} as expected")
    # else:
    #     print(f"FAILED: Expected {expected} but got {res}")

if __name__ == '__main__':
    # test_beam()
    run_day_19_1()
    # run_day_19_2()
