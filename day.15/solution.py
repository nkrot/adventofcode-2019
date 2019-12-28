#!/usr/bin/env python

# # #
# TODO: reuse day 11 PaintingRobot or 13 arcade.Game?
#

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import random

from aoc.intcode import Tape, Interpreter

import numpy as np
np.set_printoptions(linewidth=1000, threshold=np.inf)

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
        self.board = None
        self.goal_found = False

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
            # computer is the Repair Droid
            self.computer = Interpreter(self._program, self.outputs)
            self.computer.set_uplink_to(self)
        else:
            raise ValueError(f"Can not set program from object of type {type(program)}")

    def execute(self):
        self._vprint("RemoteControl running")

        while not self.finished:
            # repair droid accepts a movement instruction (0-4) and outputs status code (0-3)

            self.generate_movement_instruction()
            self.computer.execute()
            self.interpret_status_code()
            self._vprint(f"--- Board state ---\n{self.board.visualize()}\n------")

    @property
    def finished(self):
        # TODO: is the task of finding the shortest path between ORIGIN and GOAL,
        # we may need to inspect the whole board and find all possible paths.
        # Therefore, we should not stop
        #return self.computer.finished
        return self.computer.finished or self.goal_found
        #return False

    def generate_movement_instruction(self):
        """
        Decide where to move and put corresponding code into <movement_commands>.
        """

        # prefer an UNKNOWN cell over any other
        # if there are no unknown cells remaining, choose an OPEN path
        # TODO: when choosing an OPEN path, disfavour the one from where we have come
        moves = [(self.board[self.attempted_position(mc)], mc) for mc in self.MOVEMENTS]
        for g in [Board.UNKNOWN, Board.OPEN]:
            _moves = [m for m in moves if m[0] == g]
            if len(_moves) > 0:
                self.movement_command = random.choice(_moves)[1]
                break

        self.movement_commands.append(self.movement_command)
        # self._vprint(f"State of movement commands (remote control -> droid): {self.movement_commands}")

    def interpret_status_code(self):
        """
        Interpret the status code from the repair droid
        """
        # self._vprint(f"State of status codes (droid -> remote control): {self.droid_status_codes}")
        code = self.droid_status_codes.pop(0)

        pos = self.attempted_position()

        if code == self.WALL:
            self.board.mark_as(pos, Board.WALL)
            self._mark_dead_end_path()

        elif code == self.EMPTY:
            self.board.mark_as(pos, Board.OPEN)
            self._mark_dead_end_path()
            self.board.move_player_to(pos)

        elif code == self.GOAL:
            self.board.mark_as(pos, Board.GOAL)
            self.goal_found = True

        else:
            raise ValueError(f"Illegal code received from Repair Droid: {code}")

    def _mark_dead_end_path(self):
        """
        Inspect current player position and mark is as DEADEND.
        Doing this will help us direct the droid at subsequent steps by preventing
        the the droid is sent in the direction of a DEADEND.
        """

        if self.board.is_dead_end(self.board.player):
            self.board.mark_as(self.board.player, Board.DEADEND)

    def attempted_position(self, mc=None):
        """
        Position to which the Repair Droid attempted to move
        """
        mc = mc or self.movement_command

        if   mc == self.NORTH: return self.board.north_of()
        elif mc == self.SOUTH: return self.board.south_of()
        elif mc == self.WEST:  return self.board.west_of()
        elif mc == self.EAST:  return self.board.east_of()
        else:
            raise ValueError("Oh shit")

    def _vprint(self, msg):
        if self.verbose:
            print(msg)

class Board(object):

    # TODO: there is an inconsistency in how this statuses are represented:
    # some of them are in the matrix, while others are tracked via variables.

    UNKNOWN = 0  # unopened cell (initial state)
    OPEN    = 1  # pass is possible
    WALL    = 2  # wall hit, pass not possible
    GOAL    = 3  # the cell is the goal
    PLAYER  = 4  # current position of the player
    DEADEND = 5  # the cell is a deadend or belongs to a path leading to it
    ORIGIN  = 6  # initial position

    FIGURES = {
        UNKNOWN: '.',
        OPEN:    ' ',
        WALL:    '#',
        GOAL:    'G',
        PLAYER:  'D',
        DEADEND: '=',
        ORIGIN:  'O'
    }

    def __init__(self, shape, start_pos=None):
        self.shape = shape
        self.matrix = np.zeros(shape, dtype=np.int8)
        self.origin = start_pos
        self.player = self.origin # position of the player as tuple (x,y)
        self.goal = None

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, pos):
        self._origin = pos
        if pos is not None:
            self.mark_as(pos, self.OPEN) # for logical consistency

    def __getitem__(self, pos):
        return self.matrix[pos]

    def move_player_to(self, pos):
        self.player = pos

    def mark_as(self, pos, code):
        """
        Mark given position <pos> as one of OPEN|WALL|GOAL
        """
        self.matrix[pos] = code
        if code == self.GOAL:
            self.goal = pos

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
        matrix = self.matrix.copy()
        if self.player is not None:
            matrix[self.player] = self.PLAYER
        if self.origin is not None:
            matrix[self.origin] = self.ORIGIN
        return matrix

    def north_of(self, pos=None):
        return self._xy(pos or self.player, [-1, 0])

    def south_of(self, pos=None):
        return self._xy(pos or self.player, [+1, 0])

    def west_of(self, pos=None):
        return self._xy(pos or self.player, [0, -1])

    def east_of(self, pos=None):
        return self._xy(pos or self.player, [0, +1])

    def _xy(self, pos, update):
        """
        Apply given <update> vector to given position vector <pos> and return
        obtained position, as tuple (x,y)
        """
        x = pos[0] + update[0]
        y = pos[1] + update[1]
        assert 0 <= x < self.shape[0], f"Coordinate x out of bound: {x}"
        assert 0 <= y < self.shape[1], f"Coordinate y out of bound: {y}"
        return (x,y)

    def is_dead_end(self, pos):
        if pos == self.origin:
            return False

        sides = [ self.north_of(pos),
                  self.south_of(pos),
                  self.west_of(pos),
                  self.east_of(pos) ]
        sides = [ self[s] for s in sides ]
        count = sides.count(self.WALL) + sides.count(self.DEADEND)
        return count > 2

    @property
    def length_of_open_path(self):
        """
        Note that
        * the GOAL cell is not marked as OPEN
        * the ORIGIN and PLAYER cell must be marked as OPEN for the count to be correct
        """
        # print(self.matrix)
        m = np.where(self.matrix == self.OPEN, 1, 0)
        n_steps = m.sum()
        return n_steps

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
    board.move_player_to((2,4))

    print(board.visualize())


def run_day_15_1():
    """
    What is the fewest number of movement commands required to move the repair
    droid from its starting position to the location of the oxygen system?
    """

    # SOLUTION
    #Start -> Goal: (23, 23) -> (35, 39)

    print("=== Day 15, Task 1 ===")
    expected = 220

    verbose = not True
    shape = (42,42) # optimal
    start_pos = (shape[0]//2, shape[1]//2)

    remote = RemoteControl()
    remote.board = Board(shape, start_pos)

    remote.program = Tape.read_from_file("input.txt")
    remote.verbose = verbose
    # remote.computer.verbose = verbose

    remote.execute()

    print("--- Final state of the Board ---")
    print(remote.board.visualize())
    print(f"Start -> Goal: {remote.board.origin} -> {remote.board.goal}")

    # TODO/Caveat: IMO, this is not obligatorily the shortest path between ORIGIN and
    # GOAL. There can be other, shorter, paths, but the algorithm stops before it finds
    # them. However, the answer matches the expected answer as per autograder.
    res = remote.board.length_of_open_path
    print(f"Answer: distance between ORIGIN and GOAL in movements: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_tests_15_2():

    print("=== Day 15, Task 2 (tests) ===")
    pass


def run_day_15_2():
    print("=== Day 15, Task 2 ===")
    pass

if __name__ == '__main__':
    # run_tests_15_1() # ok
    run_day_15_1()

    # run_tests_15_2()
    # run_day_15_2()
