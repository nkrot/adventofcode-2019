#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from aoc.intcode import Tape, Interpreter

import numpy as np
np.set_printoptions(threshold=sys.maxsize)

class PaintingRobot(object):
    # robots language
    BLACK = 0
    WHITE = 1
    
    TLEFT = 0
    TRIGHT = 1

    def __init__(self, program, canvas):
        self.program = program
        self.verbose = False
        self.inputs = []
        self.outputs = []
        self.computer = Interpreter(self.program, self.outputs)
        #self.computer.verbose = self.verbose
        self.computer.set_uplink_to(self)
        self.canvas = canvas
        self.operations = [self.do_paint, self.do_turn]
        self.current_operation_index = -1
        self.turns = [[-1,0], [0,1], [1,0], [0,-1]] # up,right,down,left
        self.turns_index = 0
        self.running = 0 # (0,1) idle,running
        self.num_iterations = 0
        self.on_paint = None

    def move_to(self, pos):
        self.position = pos

    def execute(self):

        if self.running == 0:
            self.running = 1
            color = self.canvas[self.position]
            self.outputs.append(color)
            self._vprint(f"Robot starts over cell {self.position} of color {color}:\n{self._show_canvas()}")

        while True:
            self.num_iterations += 1
            self._vprint(f"[Iteration #{self.num_iterations}] State of input buffer: {self.inputs}")

            if len(self.inputs) == 2:
                self.do_paint(self.inputs.pop(0))
                self.do_turn(self.inputs.pop(0))
                color = self.canvas[self.position]        
                self._vprint(f"Robot ends up over cell {self.position} of color {color}:\n{self._show_canvas()}")
                self.outputs.append(color)

            elif len(self.inputs) > 2:
                self._vprint("OOPS: too many instructions in the robots input buffer")

            self._vprint(f"Running computer with inputs {self.computer.inputs} ({self.computer.status})")
            self.computer.execute()

            if self.computer.finished:
                self._vprint(f"Finished: {self.computer.finished}")
                break
    
    def read_input(self):
        code = None
        if len(self.inputs) > 0:
            code = self.inputs.pop(0)
        return arg

    def do_paint(self, color=None):
        _oldcolor = self.canvas[self.position]
        if color is None:
            color = self.inputs.pop(0)
        self.canvas[self.position] = color
        if self.on_paint is not None:
            self.on_paint(self.position, _oldcolor, color)
        self._vprint(f"Painting {self.position} from {_oldcolor} to {color}")

    def do_turn(self, code=None):
        """
        Turn acccording to the instruction and move one step
        """
        if code is None:
            code = self.inputs.pop(0)

        if   code == 0: self.turns_index -= 1
        elif code == 1: self.turns_index += 1
        
        if   self.turns_index < 0: self.turns_index = 3
        elif self.turns_index > 3: self.turns_index = 0

        step = self.turns[self.turns_index]
        self.position = (self.position[0]+step[0], self.position[1]+step[1])
        self._vprint(f"Turn code {code}, turns index {self.turns_index} is {step}, end up in {self.position}")
        
    def _set_current_operation(self):
        self.current_operation_index += 1
        if self.current_operation_index >= len(self.operations):
            self.current_operation_index = 0
        self.current_operation = self.operations[self.current_operation_index]

    def _vprint(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    def _show_canvas(self):
        kopy = np.copy(self.canvas)
        kopy[self.position] = 5
        kopy = np.array2string(kopy, max_line_width=10000)
        return kopy

################################################################################

def run_tests_day_11_1():
    print("=== Day 11 part 1 (tests) ===")
    
    # test as in task
    shape = (5,5)
    startpos = (2,2)
    
    hull = np.zeros(shape, dtype='int8') 

    tape = Tape.read_from_file("input.11.txt") # any will do
    robot = PaintingRobot(tape, hull)
    robot.move_to(startpos)

    commands = [[1,0], [0,0], [1,0], [1,0], [0,1], [1,0], [1,0]]
    for paint,turn in commands:
        robot.do_paint(paint)
        robot.do_turn(turn)

    print(robot.canvas)

def run_day_11_1():
    """
    Before you deploy the robot, you should probably have an estimate of the area it will cover:
    specifically, you need to know the number of panels it paints at least once, regardless of color. 
    Build a new emergency hull painting robot and run the Intcode program on it.
    How many panels does it paint at least once?
    """

    print("=== Day 11 part 1 (takes long to run) ===")
    
    tape = Tape.read_from_file("input.11.txt")
    expected = 2226

    shape = (100,80)
    startpos = (49,29)
    hull = np.zeros(shape, dtype='int8') # all BLACK

    robot = PaintingRobot(tape, hull)
    robot.verbose = not True

    painted_panels = {}
    def count_painted_panels(coord, oldcolor, newcolor):
        painted_panels[coord] = True

    robot.on_paint = count_painted_panels

    robot.move_to(startpos)
    robot.execute()

    # print(f"Finished after {robot.num_iterations}")
    # print(robot._show_canvas())

    res = len(painted_panels)
    print(f"Answer: number of painted panels is {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_day_11_2():
    """
    """

    print("=== Day 11 part 2 ===")
    
    tape = Tape.read_from_file("input.11.txt")
    expected = """\
...........................................
.#..#.###...##..#....####.#..#.#....####...
.#..#.#..#.#..#.#.......#.#.#..#....#......
.####.###..#....#......#..##...#....###....
.#..#.#..#.#.##.#.....#...#.#..#....#......
.#..#.#..#.#..#.#....#....#.#..#....#......
.#..#.###...###.####.####.#..#.####.#......
..........................................."""

    shape = (8,43)
    startpos = (1,0)
    hull = np.zeros(shape, dtype='int8') # all BLACK

    robot = PaintingRobot(tape, hull)
    robot.verbose = not True
    hull[startpos] = PaintingRobot.WHITE

    painted_panels = {}
    def count_painted_panels(coord, oldcolor, newcolor):
        painted_panels[coord] = True

    robot.on_paint = count_painted_panels

    robot.move_to(startpos)
    robot.execute()

    # print(f"Finished after {robot.num_iterations}")
    # print(robot._show_canvas())

    lines = []
    for row in hull:
        cols = ["." if c == 0 else "#" for c in row]
        lines.append("".join(cols))
    res = "\n".join(lines)
    # print(res) #=> HBGLZKLF

    if res == expected:
        print(f"SUCCESS: Got as expected:\n{res}")
    else:
        print(f"FAILED: Expected\n{expected}\nbut got\n{res}\n")

if __name__ == '__main__':
    # run_tests_day_11_1() # ok

    run_day_11_1() # ok
    run_day_11_2() # ok
