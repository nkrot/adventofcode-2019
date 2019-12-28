#!/usr/bin/env python

# # #
#
#

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import math
from functools import reduce
import copy
from aoc.sky import CelestialBody, physics

################################################################################

jupiter_moon_names = ["Io", "Europa", "Ganymede", "Callisto"]

def read_lines_from_file(fname):
    with open(fname) as fd:
        lines = [line.strip() for line in fd.readlines()]
    return lines

def create_celestial_bodies(lines, names=None):
    moon_names = names or [] 
    moons = []
    for line,name in zip(lines,moon_names):
        moon = CelestialBody.from_text(line, name)
        moons.append(moon)
    return moons

################################################################################

class Simulator(object):

    def __init__(self):
        self.verbose = False
        self.celestial_bodies = []
        self.num_iterations = 0

    @property
    def objects(self):
        return self.celestial_bodies

    def add_objects(self, objects):
        if isinstance(objects, list):
            self.celestial_bodies.extend(objects)
        else:
            self.celestial_bodies.append(objects)
        return len(self.celestial_bodies)

    def execute(self, times=1):
        # if self.verbose:
        #     self.print_objects()
            
        for t in range(times):
            self.num_iterations += 1
            self._vprint(f"Iteration #{self.num_iterations}")

            self._vprint(f"Computing velocity updates...")
            velocity_updates = [physics.gravity_from(obj, self.celestial_bodies)
                                for obj in self.celestial_bodies]
            # self._vprint(velocity_updates)

            self._vprint("Updating velocity and position...")
            for body,update in zip(self.celestial_bodies,velocity_updates):
                # print(body)
                # print(update)
                body.update_velocity(update)
                body.update_position()
                # print(body)

            if self.verbose:
                self.print_objects()

    def _vprint(self, msg):
        if self.verbose:
            print(msg)

    def print_objects(self):
        for body in self.celestial_bodies:
            print(repr(body))

    def system_energy(self):
        return sum([body.energy() for body in self.celestial_bodies])

def find_periods(moons):
    """
    Compute orbital periods of all given objects.

    Returns
    -------
    a list of periods (in random order)

    Side effects
    ------------
    Sets CelestialObject#period property of every object given
    """

    initial_states = [copy.deepcopy(m) for m in moons]

    simulator = Simulator()
    simulator.add_objects(moons)

    num_moons = len(moons)
    periods = []

    times = 0
    while True:
        times += 1
        simulator.execute()
        
        for prev,curr in zip(initial_states, moons):
            if curr.period is None and prev == curr:
                curr.period = times
                print(curr)
                periods.append(times)
                if len(periods) == num_moons:
                    return periods

    return periods

def lcm(*vals):
    """
    Least common multiplier for more than two variables
    """
    vals = set(vals)
    m = reduce(lambda x, y: x*y, vals)
    return m//gcd(*vals)

def gcd(*vals):
    """
    Greatest common devisor for more than two variables
    """
    vals = set(vals)
    return reduce(lambda x,y: math.gcd(x,y), vals)

################################################################################
        
def run_tests_12_1():
    lines = ["<x=-1, y=0, z=2>", "<x=2, y=-10, z=-7>", "<x=4, y=-8, z=8>", "<x=3, y=5, z=-1>" ]
    expected = 179
    
    moons = create_celestial_bodies(lines, jupiter_moon_names)

    simulator = Simulator()
    simulator.verbose = not True
    
    simulator.add_objects(moons)
    simulator.execute()
    simulator.execute(2)
    simulator.execute(7)

    res = simulator.system_energy()
    print(f"Total energy of the system: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_tests_12_2():
    """
    How many steps does it take to reach the first state that exactly matches a previous state?
    """
    lines = ["<x=-1, y=0, z=2>", "<x=2, y=-10, z=-7>", "<x=4, y=-8, z=8>", "<x=3, y=5, z=-1>" ]
    expected = 2772

    moons = create_celestial_bodies(lines, jupiter_moon_names)

    periods = find_periods(moons)
    print(f"Periods: {periods}")
    
    res = lcm(*periods)
    print(f"Number of iterations till the system comes in the same state: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_day_12_1():
    lines = read_lines_from_file("input.12.txt")
    expected = 7636

    moons = create_celestial_bodies(lines, jupiter_moon_names)

    simulator = Simulator()
    simulator.add_objects(moons)
    simulator.execute(1000)

    res = simulator.system_energy()
    print(f"Total energy of the system: {res}")
    
    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_day_12_2():
    """
    How many steps does it take to reach the first state that exactly matches a previous state?
    """

    print("=== Day 12 part 2 (runs really long) ===")

    lines = read_lines_from_file("input.12.txt")
    expected = -1

    moons = create_celestial_bodies(lines, jupiter_moon_names)

    periods = find_periods(moons)
    print(f"Periods: {periods}")
    
    res = lcm(*periods)
    print(f"Number of iterations till the system comes in the same state: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

if __name__ == '__main__':
    run_tests_12_1() # ok
    run_day_12_1()   # ok

    run_tests_12_2() # ok
    #run_day_12_2() # TODO: not solved
    
