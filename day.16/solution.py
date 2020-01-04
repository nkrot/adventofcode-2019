#!/usr/bin/env python

# # #
#
#

# import os
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# from aoc.intcode import Tape, Interpreter

import numpy as np

def fft_build_pattern(numbers):
    maxlen = len(numbers)
    base = [0, 1, 0, -1]
    pattern = np.empty(shape=[maxlen,maxlen], dtype=np.int8)

    for i in range(1, maxlen+1):
        ebase = np.repeat(base, i)
        reps = (maxlen // len(ebase))+1
        pattern[i-1:] = np.tile(ebase, reps)[1:1+maxlen]
    pattern = pattern.transpose()

    return pattern

def fft_apply_pattern(signal, pattern):
    res = np.dot(signal, pattern)
    res = np.remainder(np.abs(res), [10])
    return res

def fft_transform(numbers, times=1):
    v = np.array(numbers)
    # print(v)

    pattern = fft_build_pattern(numbers)
    # print(pattern)

    for i in range(times):
        v = fft_apply_pattern(v, pattern)

    return list(v)

def run_tests_16_1():
    print("=== Day 16, Task 1 (tests) ===")

    tests = [
        ([1,2,3,4,5,6,7,8], 4, [0,1,0,2,9,4,9,8])
    ]

    for tst in tests:
        numbers,times,expected = tst
        res = fft_transform(numbers, times)
        print(res)

        if str(res) == str(expected):
            print(f"SUCCESS: Got {res} as expected")
        else:
            print(f"FAILED: Expected {expected} but got {res}")

def read_from_file(fname):
    with open(fname) as fd:
        line = fd.read().strip()
    numbers = [int(ch) for ch in line]
    return numbers

def run_day_16_1():
    """
    After 100 phases of FFT, what are the first eight digits in the final output list?
    """

    print("=== Day 16, Task 1 ===")

    numbers = read_from_file("input.txt")
    expected = "77038830"

    full_res = fft_transform(numbers, 100)
    res = "".join([str(i) for i in full_res[0:8]])

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")


def run_tests_16_2():
    print("=== Day 16, Task 2 (tests) ===")

    res = -1
    expected = -2

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")


def run_day_16_2():
    print("=== Day 16, Task 2  ===")

    numbers = read_from_file("input.txt")
    numbers = numbers * 10000

    res = -1
    expected = -2

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

if __name__ == '__main__':
    run_tests_16_1()
    run_day_16_1()

    # run_tests_16_2()
    # run_day_16_2()
