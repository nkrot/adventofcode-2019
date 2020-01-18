#!/usr/bin/env python

# # #
# day 18
#

import numpy as np
import copy

# import os
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# from aoc.intcode import Tape, Interpreter

################################################################################

class Artifact(object):
    """
    Represents an object (artifact) on a board, one of the below:
    * a doors (uppercase letter)
    * a key (lowercase letters)
    * an entrance (@)
    """

    @classmethod
    def from_name(cls, name):
        if name.isalpha() or name == '@':
            return cls(name)
        return None

    def __init__(self, *args):
        self.x, self.y = None, None
        self.name = None

        if len(args) == 1:
            self.name = args[0]
        elif len(args) == 3:
            self.x, self.y, self.name = args
        elif len(arge) > 0:
            raise ValueError(f"Can not create {self.__class__} from {args}")

    @property
    def position(self):
        return (self.x, self.y)

    @position.setter
    def position(self, xy):
        self.x, self.y = xy

    def is_entrance(self):
        return self.name == '@'

    def is_key(self):
        return self.name.isalpha() and self.name.islower()

    def is_door(self):
        return self.name.isalpha() and self.name.isupper()

    def unlocks(self, other):
        return other.is_door() and other.name.lower() == self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}, {(self.x, self.y)}>"

class Board(object):
    WALL   = '#'
    EMPTY  = '.'
    PASSED = '='

    def copy(self):
        return copy.deepcopy(self)

    @classmethod
    def from_lines(cls, lines):
        board = Board((len(lines), len(lines[0])))
        for idx,line in enumerate(lines):
            board.set_row(idx, line)
        return board

    def __init__(self, shape):
        self.matrix = np.zeros(shape, dtype=np.int8)
        self.artifacts = {}
        self._entrance = None

    @property
    def entrance(self):
        if self._entrance is None:
            for art in self.artifacts.values():
                if art.is_entrance():
                    self.entrance = art.position
                    break
        return self._entrance

    @entrance.setter
    def entrance(self, pos):
        self._entrance = pos

    def set_row(self, i, row):
        if isinstance(row, str):
            _row = []
            for j,ch in enumerate(row):
                artifact = Artifact.from_name(ch)
                if artifact:
                    artifact.position = (i,j)
                    self.artifacts[(i,j)] = artifact
                _row.append(ord(ch))
            self.matrix[i] += _row
        else:
            raise ValueError(f"Setting from {type(row)} not supported")

    def mark_as(self, pos, val):
        self.matrix[pos] = ord(val)

    def mark_as_passed(self, pos):
        self.mark_as(pos, self.PASSED)

    def mark_as_open(self, pos):
        if pos in self.artifacts:
            del self.artifacts[pos]
        self.mark_as(pos, self.EMPTY)

    def at(self, pos):
        return self.artifacts.get(pos, chr(self.matrix[pos]))

    def visualize(self, compact=True):
        """
        Generate a string representing the board in human-readable format.
        """
        sep = {True: '', False: ' '}[compact]
        lines = []
        for i,row in enumerate(self.matrix):
            line = sep.join([chr(c) for c in row])
            # line = sep.join([str(self.at((i,j))) for j in range(len(row))])
            lines.append(line)
        pic = "\n".join(lines)
        return pic

    def open_neighbours_of(self, pos):
        neighbours = [
            ( pos[0]-1, pos[1]   ), # north
            ( pos[0]+1, pos[1]   ), # south
            ( pos[0],   pos[1]-1 ), # west
            ( pos[0],   pos[1]+1 )  # east
        ]
        positions = [pos for pos in neighbours
                     if self.at(pos) not in [self.WALL, self.PASSED]]
        return positions

    def __str__(self):
        return self.visualize()

################################################################################

class RouteMap(object):
    """
    A graph representing all paths
    """

    def __init__(self):
        self.origin = None
        self.edges = []

    def connect(self, start, end):
        edge = self.Edge(start, end)
        print(f"adding edge from {edge}")
        self.edges.append(edge)

    def __str__(self):
        lines = [ str(edge) for edge in self.edges ]
        return "\n".join(lines)

    class Edge(object):
        def __init__(self, start, end):
            self.start = start
            self.end = end

        def __str__(self):
            return f"{str(self.start)} -> {str(self.end)}"

class MazeWalker(object):
    def __init__(self):
        self.queue = []
        self.verbose = not False
        self.route_map = RouteMap()
        self.keys = []

    def copy(self):
        return copy.deepcopy(self)

    def add_key(self, k):
        if k.is_key():
            self.keys.append(k)

    def can_unlock_door(self, d):
        return d.is_door() and any(k.unlocks(d) for k in self.keys)

    def all_paths(self, board):
        board = board.copy()
        self._walk(board, self.route_map)

    def _walk(self, board, route):
        board.mark_as_open(board.entrance)
        ends = self._explore_maze(board)
        print(ends)
        for end in ends:
            key_or_door = board.at(end)
            # print(repr(key_or_door))

            if key_or_door.is_key() or self.can_unlock_door(key_or_door):
                newboard = board.copy()
                newboard.entrance = end

                walker = self.copy()
                walker.add_key(key_or_door)
                walker.route_map = route
                walker.all_paths(newboard)

    # TODO: additionally count the distance from origin to every reached end
    def _explore_maze(self, board):
        origin = board.entrance
        if self.verbose:
            print(f"--- walk from {origin} ---")
        queue, passed = [origin], [origin]
        stops = []
        while len(queue):
            _origin = queue.pop(0)
            for pos in board.open_neighbours_of(_origin):
                if pos in passed:
                    continue
                point = board.at(pos)
                if point == board.EMPTY:
                    #self.board.mark_as_passed(pos)
                    passed.append(pos)
                    queue.append(pos)
                elif isinstance(point, Artifact):
                    stops.append(pos)
                    self.route_map.connect(origin, pos)
                else:
                    raise ValueError(f"Oops. Dont know what to do with {point} at {pos}")
        if self.verbose:
            print(board)
        return stops

################################################################################

text = """
##########################
#f.D.E.e.C.b.A...@.a.B.c.#
########################.#
#d.......................#
##########################
"""

def run_test_artifacts():
    print("=== Tests of Artifact object ===")

    door_A   = Artifact("A")
    door_A.position = (2, 20)
    key_a    = Artifact(1,10,"a")
    key_b    = Artifact(3,30,"b")
    entrance = Artifact("@")

    print(repr(door_A))
    print(repr(key_b))

    print(key_a.is_key() == True)
    print(key_a.is_door() == False)

    print(door_A.is_key() == False)
    print(door_A.is_door() == True)
    print(door_A.position == (2,20))

    print(key_a.unlocks(door_A)  == True)
    print(key_b.unlocks(door_A)  == False)
    print(door_A.unlocks(door_A) == False)

    print(entrance.is_key()  == False)
    print(entrance.is_door() == False) # TODO: strictly speaking, an entrance is a Door


def run_tests_18_1():
    print("=== Day 18, Task 1 (tests) ===")

    lines = [line for line in text.split('\n') if line]

    b = Board.from_lines(lines)
    print(b)

    walker = MazeWalker()
    walker.verbose = True
    walker.all_paths(b)

    print(walker.route_map)

if __name__ == '__main__':
    # run_test_artifacts()

    run_tests_18_1()
    # run_day_18_1()
