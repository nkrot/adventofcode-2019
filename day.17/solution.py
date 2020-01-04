#!/usr/bin/env python

# # #
# TODO
# 1. rename BoardBuilder to VideoDisplay?
# 2. refactor CommandEncoder:
#    * name things meaningfully
#    * do not generate what is not required
# 4. implement computing the path (now hardcoded in BoardBuilder.path)

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import random

from aoc.intcode import Tape, Interpreter

from copy import deepcopy
import numpy as np
from pprint import pprint

import itertools # danger! python's coprophagy is imported

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
        s2 = "L,9,3,R,12,L,9,1,L,9,1,L,9,3,R,6,L,8"

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
        self.max_components = max_components
        self.max_length = max_length
        self.subsequences = []
        self.function_names = {0: 'A', 1: 'B', 2: 'C'}

    def execute(self, seq):
        if isinstance(seq, type([])):
            items = deepcopy(seq)
        else:
            items = seq.split(',')
        self.decompose(items, [], [])

    def decompose(self, items, parts, part_ids):
        """
        Given a sequence (a list <items>), find a number of subsequence from which
        the original sequence can be constructed such that
        * subsequences can be repeated
        * the number of subsequences does not exceed <self.max_components>
        * the length of each subsequence does not exceed <self.max_length>
        """

        if len(items) == 0:
            self.subsequences.append( (deepcopy(parts), deepcopy(part_ids)) )
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
                self.decompose(tail, parts, part_ids)
                part_ids.pop()

            if added:
                parts.pop()

        return True

    def to_strings(self, subsequence):
        """
        Convert <subsequence> (as those stored in self.subsequences) to strings
        TODO: this is ugly
        """
        _parts, _names = subsequence
        names = self._add_commas([self.function_names[n] for n in _names])
        parts = [self._add_commas(part) for part in _parts]
        return ["".join(names)] + [ "".join(p) for p in parts]

    def to_tapes(self, subsequence):
        """
        TODO: this is ugly
        """
        ss = self.to_strings(subsequence)
        tapes = []
        for s in ss:
            tape = Tape()
            tape.append(list(s+'\n'), ord)
            tapes.append(tape)
        return tapes

    def _add_commas(self, elems):
        # DANGER: python coprophagy!
        elems_with_commas = list(itertools.chain.from_iterable(zip(elems, [',']*len(elems))))
        elems_with_commas.pop()
        return elems_with_commas

################################################################################

def run_tests_17_2():
    bb = BoardBuilder()

    tests = [
        ("R,8,R,8,R,4,R,4,R,8,L,6,L,2,R,4,R,4,R,8,R,8,R,8,L,6,L,2",
         ["A,B,C,B,A,C", "R,8,R,8", "R,4,R,4,R,8", "L,6,L,2"],
         ["65,44,66,44,67,44,66,44,65,44,67,10",
          "82,44,56,44,82,44,56,10",
          "82,44,52,44,82,44,52,44,82,44,56,10",
          "76,44,54,44,76,44,50,10"]),

        # TODO: solved manually
        (bb.path,
         ['A,A,B,C,B,C,B,C,B,A', 'R,6,L,9,3,R,6', 'L,9,3,R,6,L,8,L,9,3', 'R,12,L,9,1,L,9,1'],
         ['65,44,65,44,66,44,67,44,66,44,67,44,66,44,67,44,66,44,65,10',
          '82,44,54,44,76,44,57,44,51,44,82,44,54,10',
          '76,44,57,44,51,44,82,44,54,44,76,44,56,44,76,44,57,44,51,10',
          '82,44,49,50,44,76,44,57,44,49,44,76,44,57,44,49,10'])
    ]

    for tst,exp,exp_ascii in tests:
        enc = CommandEncoder(3, 10)
        enc.execute(tst)

        ok = False
        fails = []
        for idx,subseq in enumerate(enc.subsequences):
            res = enc.to_strings(subseq)
            res_ascii = [str(t) for t in enc.to_tapes(subseq)]
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

    enc = CommandEncoder(3, 10)
    enc.execute(path)

    # TODO: movement instructions are given as a sequence of individual integers
    # (now available as Tape.cells). CommandEncoder can now be simplified.
    print(f"Number of command variations: {len(enc.subsequences)}")
    decomposition = enc.subsequences[0]
    commands = []
    for t in enc.to_tapes(decomposition):
        commands.extend(list(t.cells))

    # provide continuous video feed?
    # continous video feed will produce a full board after each robot movement
    # This is very slow!
    yes = [ord('y'), ord('\n')]
    no =  [ord('n'), ord('\n')]
    commands.extend(no)

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
