#!/usr/bin/env python

# # #
# TODO
# 1. Scanner and Beam use transposed coordinates
#    Scanner: x is horizontal offset, y is vertical offset (as in the task definition)
#    Beam: x is vertical offset (top-to-bottom) and y is horizontal (like in numpy matrix)
# 2. part 2 runs 80 minute!

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

        # the ship we are looking for has the following size
        self.target_v = 100 # vertical size
        self.target_h = 100 # horizontal size
        self.target = None  # coordinates of the top left corner of the target found

    # TODO
    # this is executed too often, although it should be enough to do it
    # once after completing one layer.
    def finished(self):
        width = 0
        front_edge = self.beam.layer(-1)
        if front_edge:
            width = len(front_edge[1])
            if width >= self.target_h:
                back_edge = self.beam.layer(-self.target_v)
                # print("Check size")
                # TODO: sorting is performed too often. Can Beam sort a layer
                # itself and do it only once?
                front_edge_hs = sorted(front_edge[1])[:self.target_h]
                back_edge_hs  = sorted(back_edge[1])
                h_idx = back_edge_hs.index(front_edge_hs[0])
                back_edge_hs = back_edge_hs[h_idx:h_idx+self.target_h]
                # print(back_edge)
                # print(front_edge)
                if back_edge_hs == front_edge_hs:
                    # print(back_edge_hs)
                    # print(front_edge_hs)
                    self.target = (front_edge_hs[0], back_edge[0]) # in (hor,vert) order!
                    # print(f"SOLUTION: {self.target}")
                    return True
        return width > 2*self.target_h # to evoid infinite loop

class Beam(object):
    """class that represents the tractor beam"""

    FIGURES = {
        0: '.',  # drone is stationary
        1: '#',  # drone is pulled
        2: '-',  # checked
    }

    def __init__(self, maxlayers=None):
        self.area = 0
        self.layers = defaultdict(list)
        self.maxlayers = maxlayers

    def __contains__(self, coord):
        v,h = coord
        row = self.layers.get(v, [])
        return h in row

    def add(self, coord):
        """
        Adds given point to beam. A point is given as a tuple:
        (vertical_coordinate, horizontal_coordinate)
        """
        # print(f"adding: {coord}")
        vert, hor = coord
        self.area += 1 # TODO: will be wrong if a duplicate is added
        # to avoid triggering layer-trimming logic too often, we now decide if
        # we need to do it now that we will add a new point:
        # does the point being added belongs to a *new* layer or an existing one?
        # if adding a point creates a new layer, then we will want to perform
        # trimming.
        trim_layer = self.maxlayers and vert not in self.layers
        self.layers[vert].append(hor)
        if trim_layer:
            self._trim_oldest_layer()
        return self

    def layer(self, offset=-1):
        """
        Get layer in form of a tuple (x, [y1,y2,...,y4]) at given offset from
        the edge of the beam. If offset=-1, returns the edge.
        """
        assert offset < 0, \
            "Offset must be less than 0 (like in backward list indexing)"
        res = None
        if len(self.layers) >= abs(offset):
            xs = sorted(self.layers.keys()) # TODO: how to do it less often?
            x = xs[offset]
            res = (x, self.layers[x])
        return res

    def __str__(self):
        return self.visualize()

    def visualize(self, compact=True):
        sep = {True: '', False: ' '}[compact]
        lines = []
        # get vertical min,max and horizontal min,max
        vs = self._minmax(self.layers.keys())
        hs = self._minmax(list(chain.from_iterable(self.layers.values())))
        for v in range(vs[0], 1+vs[1]):
            row = []
            for h in range(hs[0], 1+hs[1]):
                if h in self.layers.get(v, []):
                    row.append(self.FIGURES[1])
                else:
                    row.append(self.FIGURES[0])
            lines.append(sep.join(row))
        return "\n".join(lines)

    def _trim_oldest_layer(self):
        vs = self._minmax(self.layers.keys())
        n = 1 + vs[1] - vs[0] - self.maxlayers
        if n > 0:
            # this should be sufficient if the beam grows continuously
            del self.layers[vs[0]]

    #def _trim_old_layers(self):
        # vs = self._minmax(self.layers.keys())
        # num_layers = vs[1] - vs[0] # 10 - 3 = 7
        # n = self.maxlayers - num_layers
        # if n > 0:
        #     print(f"deleting {n} initial layers")
        #     keys = sorted(self.layers.keys())[:n]
        #     print(keys)

    def _minmax(self, lst):
        return min(lst), max(lst)

def test_beam():
    beam = Beam(5)
    points = [(4,5), (5,4), (6,5), (7,7), (7,6), (8,6), (8,7), (9,7), (10,8),
              (11,9), (12, 10), (12,11)]
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
    """
    TODO: runs really long: 80 min
    """
    print("=== Day 16, Task 2 (takes really long) ===")

    tape = Tape.read_from_file('input.txt')
    expected = 6950903

    scanner = Scanner2(tape)
    scanner.verbose = not True
    beam = Beam(scanner.target_v)
    scanner.execute(beam)

    # print("--- results ---")
    # print(beam)
    print(f"Coordinates of the closest point: {scanner.target}")

    x,y = scanner.target # (695,903)
    res = 10000*x+y      # 6950903

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

if __name__ == '__main__':
    # test_beam()
    run_day_19_1()
    run_day_19_2()
