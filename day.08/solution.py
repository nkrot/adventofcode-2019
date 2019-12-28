#!/usr/bin/env python

# # #
#
#

import numpy as np
from collections import Counter

# converting a list to a list of sublists of specific length
# #chunks = [data[x:x+100] for x in xrange(0, len(data), 100)]

HEIGHT, WIDTH = 6, 25

def read_from_file(fname):
    with open(fname) as fd:
        lines = [l.strip() for l in fd.readlines()]
    return lines[0]

def get_layers(digits, dims=None):
    if dims is None:
        dims = (HEIGHT, WIDTH)
    num_layers = len(digits) / (dims[0] * dims[1])
    layers = np.array_split(np.array(digits), num_layers)
    # print("Number of layers: {}".format(len(layers)))
    return layers

def run_day_8_1():
    """
    what is the number of 1 digits multiplied by the number of 2 digits?
    """

    print("=== Day 8 part 1 ===")

    line = read_from_file('input.txt')
    digits = [int(ch) for ch in line]
    expected = 2250

    layers = get_layers(digits, (HEIGHT, WIDTH))

    nonzero_counts = [np.count_nonzero(layer) for layer in layers]

    min_zero_count = max(nonzero_counts)
    # print(min_zero_count)

    num_layers_with_min_zero_count = nonzero_counts.count(min_zero_count)
    # print("Number of layers with min zero count {} (must be 1)".format(
    #     num_layers_with_min_zero_count))
    assert num_layers_with_min_zero_count == 1, "Ambiguous!"

    layer = layers[nonzero_counts.index(min_zero_count)]
    # print(layer)

    counts = Counter(layer)
    answer = counts[2] * counts[1]

    print(f"Answer: {answer}")

    if expected == answer:
        print(f"SUCCESS: Got {answer} as expected.")
    else:
        print(f"FAILED: Expected {expected} but got {answer}.")

def overlay_layers(layers):
    res = layers[0].copy()
    for i in range(1, len(layers)):
        for j in range(0, len(res)):
            #res[j] += layers[i][j] # ok, works like sum
            l, r = res[j], layers[i][j]
            if l == 2:
                res[j] = r
    return res

def run_tests_8_1():
    print("=== Day 8 part 1 (tests_ ===")

    tests = [
        ("0222112222120000", (2,2), [0,1,1,0])
    ]

    for test in tests:
        s, dims = test[:2]
        expected = test[2]

        digits = [int(ch) for ch in s]
        layers = get_layers(digits, dims)
        # print(layers)

        res = overlay_layers(layers)
        print(f"Final image looks like: {res}")

        cmp = expected == res # e.g. [True True True False]

        if np.all(cmp):
            print(f"SUCCESS: Got {res} as expected.")
        else:
            print(f"FAILED: Expected {expected} but got {res}.")

def visualize(image):
    for row in image:
        print("".join(["B" if i == 1 else " " for i in row]))

def run_day_8_2():
    """
    """

    print("=== Day 8 part 2 ===")
    
    # Solution:
    # get the layers
    # combine them in one elementwise by the rule (CL stands for any number except 2
    # that means transparent)
    #  2   + CL  --> CL
    #  CL1 + CL2 --> CL1 (keep the first CL value)

    # TODO:
    # numpy.vectorize
    # ufuncs
    # https://scipy-lectures.org/intro/numpy/operations.html

    line = read_from_file('input.txt')
    digits = [int(ch) for ch in line]
    # expected: FHJUL
    expected = "111101001000110100101000010000100100001010010100001110011110000101001010000100001001000010100101000010000100101001010010100001000010010011000110011110"

    layers = get_layers(digits, (HEIGHT, WIDTH))
    res_layer = overlay_layers(layers)

    print(res_layer)

    image = get_layers(res_layer, (1, WIDTH))
    visualize(image)

    res = "".join([str(i) for i in res_layer])
    if  res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

if __name__ == '__main__':
    run_tests_8_1() # ok

    run_day_8_1() # ok
    run_day_8_2() # ok
