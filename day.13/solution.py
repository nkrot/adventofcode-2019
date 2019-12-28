#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from aoc.intcode import Tape, Interpreter
from aoc.arcade import Game, PlayerFollower as Player

import numpy as np

################################################################################

def run_tests_13_1():
    print("=== Day 13 part 1 (tests) ===")
    steps = [[1,2,3], [6,5,4]]
    game = Game((10,10))
    
    for st in steps:
        game.draw(*st)

    print(game)

def run_day_13_1():
    """
    Start the game. How many block tiles are on the screen when the game exits?
    """
    
    print("=== Day 13 part 1 ===")
    
    tape = Tape.read_from_file("input.13.txt")
    expected = 200
    
    game = Game((45,20), tape)
    game.verbose = True
    game.execute()

    print(game)

    blocks = np.where(game.board == game.BLOCK, 1, 0)
    res = np.count_nonzero(blocks)

    print(f"Answer: number of BLOCK tiles on the board: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_day_13_2():
    """
    Beat the game by breaking all the blocks. 
    What is your score after the last block is broken?
    """
    
    print("=== Day 13 part 2 ===")
    
    tape = Tape.read_from_file("input.13.txt")
    tape.cells[0] = 2
    expected = 9803

    game = Game((45,20), tape)
    game.verbose = not True
    game.player = Player()

    game.execute()

    print("--- Final State of the Board ---")
    print(game)

    res = game.score
    print(f"Answer: The score after all blocks are destroyed is {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

if __name__ == '__main__':
    run_tests_13_1() # ok
    run_day_13_1()   # ok

    run_day_13_2() # ok
