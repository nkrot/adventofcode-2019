#!/usr/bin/env python

# # #
# TODO
# 1. rename BoardBuilder to VideoDisplay or CleaningRobot?
# 2. implement computing the path (now hardcoded in BoardBuilder.path)

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from aoc.intcode import Tape, Interpreter

import random
import numpy as np
from copy import deepcopy

class Board(object):
    SCAFFOLD = 35
    OPEN     = 46

    def __init__(self):
        self.matrix = None

    @property
    def total_alignment(self):
        intersections = self.find_intersections()
        # print(f"--- intersections {len(intersections)} ---")
        # print(intersections)
        return sum([x*y for x,y in intersections])

    def visualize(self):
        # print(f"Board shape: {matrix.shape}")
        lines = []
        for row in self.matrix:
            line = " ".join([chr(c) for c in row])
            lines.append(line)
        return "\n".join(lines)

    def find_intersections(self):
        intersections = []
        for point in zip(*np.where(self.matrix == self.SCAFFOLD)):
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
            if 0 <= new_x < self.matrix.shape[0] and 0 <= new_y < self.matrix.shape[1]:
                val = self.matrix[new_x, new_y]
                if cond is not None and not cond(val):
                    continue
                results.append((new_x, new_y, val))
        return results

    @property
    def path(self):
        """
        TODO: compute it
        """
        # from the beginning ^
        s1 = "R,6,L,9,3,R,6,R,6,L,9,3,R,6,L,9,3,R,6,L,8"

        #from position 5, 6 and 7
        s2 = "L,9,3,R,9,3,L,9,1,L,9,1,L,9,3,R,6,L,8"

        # from position 8
        s3 = "L,9,3,R,6,L,9,3,R,6"

        chunks = [s1,  s2,s2,s2,  s3]
        return ",".join(chunks).split(',')

class BoardBuilder(object):

    def __init__(self, tape=None):
        self.inputs = []
        if tape is not None:
            self.computer = Interpreter(tape)
            self.computer.set_uplink_to(self)
        self.board = None
        self.amount_of_dust = 0

    def execute(self):
        rows = []
        row = []

        while not self.computer.finished:
            self.computer.execute()

            while len(self.inputs) > 0:
                code = self.inputs.pop(0)

                if code > 127:
                    # Here we catch the value that is not the image pixel but the amount
                    # of dust the robot has collected, as per the instruction:
                    # > Once the cleanong robot finishes the programmed set of movements
                    # > it will return to its docking station and report the amount of space
                    # > dust it collected as a large, non-ASCII value in a single output
                    # > instruction.
                    self.amount_of_dust = code
                else:
                    ch = chr(code)
                    print(ch, end='', flush=True)

                    if chr(code) == '\n':
                        if len(row) > 0:
                            rows.append(row)
                        row = []
                    else:
                        row.append(code)

        self.board = Board()
        self.board.matrix = np.array(rows)

        return self.board

class CommandEncoder(object):

    def __init__(self, max_components=None, max_length=None):
        self.max_components = max_components or 3
        self.max_length = max_length or 10
        self.decompositions = []
        self.function_names = {0: 'A', 1: 'B', 2: 'C'}

    def analyse_path(self, seq):
        if isinstance(seq, type([])):
            items = deepcopy(seq)
        else:
            items = seq.split(',')
        self._decompose(items, [], [])

    def _decompose(self, items, parts, part_ids):
        """
        Given a sequence (a list <items>), find a number of subsequence from which
        the original sequence can be constructed such that
        * decompositions can be repeated
        * the number of decompositions does not exceed <self.max_components>
        * the length of each subsequence does not exceed <self.max_length>
        Results
        * is a list of tuples, where each tuple represents one possible decomposition
        * each tuple (decomposition) contains: a list of decompositions and a list of
          subsequence indices such that, when referenced decompositions are combined,
          the whole original sequence (<items>) is obtained.
        """

        if len(items) == 0:
            self.decompositions.append( (deepcopy(parts), deepcopy(part_ids)) )
            return True

        level = len(part_ids)
        indent = " " * level

        for l in range(1, 1+min(self.max_length, len(items))):
            head, tail = items[0:l], items[l:]
            # print(f"{indent}[{level}]HEAD: {','.join(head)}")
            # print(f"{indent}[{level}]TAIL: {','.join(tail)}")

            added = False
            if head not in parts and len(parts) < self.max_components:
                parts.append(head)
                added = True

            if head in parts:
                part_ids.append(parts.index(head))
                self._decompose(tail, parts, part_ids)
                part_ids.pop()

            if added:
                parts.pop()

        return True

    def to_tape(self, items):
        """
        Build a Tape from list of strings given in <items>, inserting a comma between
        individual items and adding a newline after the last item.
        """
        tape = Tape()
        separators = [','] * (len(items)-1) + ['\n']
        for item,sep in zip(items,separators):
            tape.append(item, ord)
            tape.append(sep, ord)
        return tape

    def to_tapes(self, decomposition):
        """
        Converts one decomposition (a tuple of lists as explained in self._decompose())
        a list of Tapes in the order
         at 0: tape with main function
         at 1: tape with function A
         at 2: tape with function B
         at 3: tape with function C
        Please refer to task.txt for definition of main function and functions A, B, C
        """
        tapes = []

        # main function
        names = [self.function_names[n] for n in decomposition[1]]
        tapes.append(self.to_tape(names))

        # functions
        for p in decomposition[0]:
            tapes.append(self.to_tape(p))

        return tapes

################################################################################

def run_tests_17_2():
    board = Board()

    tests = [
        ("R,8,R,8,R,4,R,4,R,8,L,6,L,2,R,4,R,4,R,8,R,8,R,8,L,6,L,2",
         ["A,B,C,B,A,C\n", "R,8,R,8\n", "R,4,R,4,R,8\n", "L,6,L,2\n"],
         ["65,44,66,44,67,44,66,44,65,44,67,10",
          "82,44,56,44,82,44,56,10",
          "82,44,52,44,82,44,52,44,82,44,56,10",
          "76,44,54,44,76,44,50,10"]),

        (board.path,
         ['A,A,B,C,B,C,B,C,B,A\n', 'R,6,L,9,3,R,6\n', 'L,9,3,R,6,L,8,L,9,3\n',
          'R,9,3,L,9,1,L,9,1\n'],
         ['65,44,65,44,66,44,67,44,66,44,67,44,66,44,67,44,66,44,65,10',
          '82,44,54,44,76,44,57,44,51,44,82,44,54,10',
          '76,44,57,44,51,44,82,44,54,44,76,44,56,44,76,44,57,44,51,10',
          '82,44,57,44,51,44,76,44,57,44,49,44,76,44,57,44,49,10'])
    ]

    def chr_tape(tape):
        return "".join([chr(val) for val in tape.cells])

    for tst,exp,exp_ascii in tests:
        enc = CommandEncoder(3, 10)
        enc.execute(tst)

        ok = False
        fails = []
        for idx,solution in enumerate(enc.decompositions):
            tapes = enc.to_tapes(solution)
            res       = [chr_tape(t) for t in tapes]
            res_ascii = [str(t)      for t in tapes]
            if res == exp and res_ascii == exp_ascii:
                ok = True
                print(f"SUCCESS: Got as expected:\n{res}\n{res_ascii}")
            else:
                fails.append(repr(res))
                fails.append(repr(res_ascii))

        if not ok:
            shit = "\n".join(fails)
            msg = f"FAILED: Expected {res} but got {len(fails)} non-matches:\n{shit}"
            print(msg)

def run_day_17_1():
    """
    What is the sum of the alignment parameters for the scaffold intersections?
    """

    print("=== Day 17, Task 1 ===")

    tape = Tape.read_from_file("input.txt")
    expected = 13580

    bb = BoardBuilder(tape)
    board = bb.execute()

    res = board.total_alignment
    print(f"Answer: sum of all camera alignment parameters: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_day_17_2():
    """
    After visiting every part of the scaffold at least once,
    how much dust does the vacuum robot report it has collected?
    """
    print("=== Day 17, Task 2 ===")

    expected = 1063081

    # first, we need to rerun the task 1 to get the board.
    #tape = Tape.read_from_file("input.txt")
    #bb = BoardBuilder(tape)
    #board = bb.execute()
    #path = board.path
    # but we are lazy and therefore cutting short
    path = Board().path

    # now part 2
    tape = Tape.read_from_file("input.txt")
    tape.write_to(0,2)

    # analyse path through the whole scaffold area and produce a program for
    # the cleaning robot that comprises movement instructions.
    commands = []
    enc = CommandEncoder()
    enc.analyse_path(path)
    print(f"Number of possible programms: {len(enc.decompositions)}")
    for t in enc.to_tapes(enc.decompositions[0]):
        commands.extend(list(t.cells))

    # provide continuous video feed?
    # continous video feed will produce a full board after each robot movement
    yes = [ord('y'), ord('\n')] # This is very slow!
    no =  [ord('n'), ord('\n')]
    commands.extend(no)

    # finally, launch the robot
    bb = BoardBuilder(tape)
    bb.computer.inputs = commands
    bb.execute()

    res = bb.amount_of_dust
    print(f"Answer: amount of dust the robot collected: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_tests_create_tape():
    tape = Tape()
    data = ["A", "B", "C", "B", "C", "A", "\n"]
    expected = "65,66,67,66,67,65,10"

    for ch in data:
        tape.append(ch, ord)

    res = str(tape)
    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

    tape = Tape()
    data = ["R", ",", "8", ",", "L", ",", "6", "\n"]
    expected = "82,44,56,44,76,44,54,10"

    tape.append(data, ord)

    res = str(tape)
    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

################################################################################

if __name__ == '__main__':
    # run_day_17_1() # ok

    # run_tests_create_tape()

    # run_tests_17_2()
    run_day_17_2()
