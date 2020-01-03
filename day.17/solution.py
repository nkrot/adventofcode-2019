#!/usr/bin/env python

# # #
# TODO
# 0. how to capture the output of the robot (the last value it outputs)?
# 1. refactor CommandEncoder:
#    * name things meaningfully
#    * do not generate what is not required
# 2. what does 'continuous video feed' does?
# 3. implement computing the path (now hardcoded in BoardBuilder.path)

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import random

from aoc.intcode import Tape, Interpreter

from copy import deepcopy
import numpy as np
from pprint import pprint

import itertools # danger! python's coprophagy is imported

class BoardBuilder(object):

    SCAFFOLD = 35
    OPEN     = 46
    
    def __init__(self, tape=None):
        if tape is not None:
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

        # TODO: dont know if this is correct...
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

def run_day_17_2():
    """
    After visiting every part of the scaffold at least once, 
    how much dust does the vacuum robot report it has collected?
    """

    expected = 1063081

    bb = BoardBuilder()
    enc = CommandEncoder(3, 10)
    enc.execute(bb.path)

    print(f"Number of command variations: {len(enc.subsequences)}")
    decomposition = enc.subsequences[0]
    commands = []
    for t in enc.to_tapes(decomposition):
        commands.extend(list(t.cells))

    # provide continuous video feed
    yes = [ord('y'), ord('\n')]
    no =  [ord('n'), ord('\n')]
    commands.extend(no)
    
    tape = Tape.read_from_file("input.txt")
    tape.write_to(0,2)
    
    computer = Interpreter(tape, commands)
    computer.execute()

    res = -1
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
    # run_day_17_1()

    #run_tests_create_tape()

    # run_tests_17_2()
    run_day_17_2()
