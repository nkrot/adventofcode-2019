#!/usr/bin/env python

# # #
# TODO
# - add a map drawing functionality
# - reuse sky.CelestialObject instead of Asteroid

import math
from itertools import groupby

debug = False

class Asteroid(object):

    @classmethod
    def compute_declension(cls, obj, origin):
        # print(f"DECL BETWEEN: {obj} and {origin}")
        decl = []
        for c1,c2 in zip(obj, origin):
            d = c1 - c2
            decl.append(d)
        gcd = math.gcd(*decl)
        if gcd != 0:
            decl = [int(c/gcd) for c in decl]
        return decl

    @classmethod
    def distance_between(self, a, b):
        return math.sqrt((a.x - b.x)**2 + (a.y-b.y)**2)

    # Quarters and sign of declension w.r.t. origin
    #
    # (-,-) | (+,-)
    #  4    |  1
    # ------o--------
    # (-,+) | (+,+)
    #  3    |  2
    # a point on a axis belongs to the quarter +1. this is correct, because
    # the laser starts shooting upwards
    @classmethod
    def compute_quarter(cls, coord):
        tests = [n >= 0 for n in coord.declension]
        q = 4
        if   tests == [True,  False]: q = 1
        elif tests == [True,  True]:  q = 2
        elif tests == [False, True]:  q = 3
        return q

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = None
        self.distance = None   # distance to origin
        self.declension = None # w.r.t. origin
        self.skyquarter = None # in what Sky quarter is the object located

    @property
    def position(self):
        return (self.x, self.y)
    
    def __iter__(self):
        return iter([self.x, self.y])

    def __str__(self):
        msg = f"coord={(self.x, self.y)}, declension={self.declension}, "
        msg += f"skyquarter={self.skyquarter}, distance={self.distance}"
        return msg

    def __repr__(self):
        return f"<{self.__class__.__name__}: {str(self)}, id={self.id}>"

    def is_at(self, coord):
        if isinstance(coord, type(self)):
            coord = (coord.x, coord.y)
        return (self.x, self.y) == coord

################################################################################

def build_asteroid_map(lines):
    if isinstance(lines, type([])):
        asteroids = []
        for y,line in enumerate(lines):
            for x,ch in enumerate(line):
                if ch == "#":
                    c = Asteroid(x,y)
                    asteroids.append(c)
        for n,ast in enumerate(asteroids):
            ast.id = n
        return asteroids
    else:
        _lines = [l.strip() for l in lines.split('\n')]
        return build_asteroid_map(_lines)

def group_by_declension(asteroids):
    groups = []
    get_decl = lambda x: x.declension
    for k,grp in groupby(sorted(asteroids, key=get_decl), key=get_decl):
        groups.append(list(grp))
    return groups

def count_visible_from(asteroids, origin):
    for ast in asteroids:
        ast.declension = Asteroid.compute_declension(ast, origin)
    return len(group_by_declension(asteroids)) - 1

def in_order_of_appearance(ast):
    decl = ast.declension
    val = ((decl[0]+0.1) / (decl[1]+0.1)) # to avoid division by 0
    return val * -1

################################################################################

def read_from_file(fname):
    """
    Read lines from given file
    """
    
    with open(fname) as fd:
        lines = fd.readlines()
    lines = [ line.strip() for line in lines ]

    return lines

def find_best_location(asteroids):
    counts = [ (origin, count_visible_from(asteroids, origin)) for origin in asteroids ]
    # for ast,cnt in counts:
    #     print(f"From {ast}: {cnt}")

    best = max(counts, key=lambda x: x[1])

    print("Best Location is:")
    print(best[0])
    print(f"Observes {best[1]} asteroids (excluding self)")

    return best

def shoot_asteroids(asteroids, center):
    
    for i in range(len(asteroids)):
        ast = asteroids[i]
        if ast.is_at(center):
            origin = ast
            asteroids.pop(i)
            break

    for ast in asteroids:
        ast.declension = Asteroid.compute_declension(ast, origin)
        ast.distance   = Asteroid.distance_between(ast, origin)
        ast.skyquarter = Asteroid.compute_quarter(ast)
        # print(ast)

    groups = group_by_declension(asteroids)

    quarters = {}
    for grp in groups:
        grp.sort(key=lambda x: x.distance)
        quarters.setdefault(grp[0].skyquarter, []).append(grp)

    # within each quarter, the groups are sorted in the order they will appear
    # to the laser/observer
    for qt in sorted(quarters.keys()):
        grps = quarters[qt]
        #print(f"QUARTER {qt}, has {len(grps)} rays")
        if len(grps) > 0:
            grps.sort(key=lambda grp: in_order_of_appearance(grp[0]))

    if debug:
        print("--- DEBUG ---")
        for qt in sorted(quarters.keys()):
            grps = quarters[qt]
            print(f"QUARTER {qt}")
            for grp in grps:
                print(f"GRP: {grp}")

    # shoot asteroids
    # print(f"Initial number of asteroids: {len(asteroids)}")
    doit = len(asteroids) > 0
    rotation, count = 0, 0
    shot_asteroids = []
    while doit:
        rotation += 1
        doit = False
        for qt in sorted(quarters.keys()):
            for grp in quarters[qt]:
                if len(grp) > 0:
                    count += 1
                    doit = True
                    ast = grp.pop(0)
                    shot_asteroids.append(ast)
                    # print(f"Count={count} at rotation={rotation}: {ast}")

    return shot_asteroids

################################################################################

def run_tests_10_1():
    print("=== Day 10 part 1 (tests) ===")

    # test data
    tests = [
        (".#..#\n.....\n#####\n....#\n...##", 8)
    ]
    
    for tst in tests:
        data, expected = tst
        asteroids = build_asteroid_map(data)
        best = find_best_location(asteroids)
        
        res = best[-1]
        if res == expected:
            print(f"SUCCESS: Got {res} as expected")
        else:
            print(f"FAILED: Expected {expected} but got {res}")

def run_day_10_1():
    """
    Find the best location for a new monitoring station.
    How many other asteroids can be detected from that location?
    """

    print("=== Day 10 part 1 ===")

    data = read_from_file("input.txt")
    expected = 274

    asteroids = build_asteroid_map(data)
    best = find_best_location(asteroids)

    res = best[-1]
    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_tests_10_2():
    print("=== Day 10 part 2 (tests) ===")

    # Testcase
    # .#....#####...#..
    # ##...##.#####..##
    # ##...#...#.#####.
    # ..#.....X...###..
    # ..#.#.....#....##

    # Expected, scheme 1
    # .#....###24...#..
    # ##...##.13#67..9#
    # ##...#...5.8####.
    # ..#.....X...###..
    # ..#.#.....#....##

    # Expected, scheme 2
    # .#....###.....#..
    # ##...##...#.....#
    # ##...#......1234.
    # ..#.....X...5##..
    # ..#.9.....8....76

    # Expeded, scheme 3
    # .8....###.....#..
    # 56...9#...#.....#
    # 34...7...........
    # ..2.....X....##..
    # ..1..............

    data = ".#....#####...#..\n##...##.#####..##\n##...#...#.#####.\n..#.....#...###..\n..#.#.....#....##"
    center = (8,3)
    
    tests = [
        # scheme 1
        (0,  (8,1)),  (1,   (9,0)), (2, (9,1)),  (3,  (10,0)), (4,  (9,2)),  (5,  (11,1)),
        (6,  (12,1)), (7,  (11,2)), (8,  (15,1)),
        # scheme 2
        (9,  (12,2)), (10, (13,2)), (11, (14,2)), (12, (15,2)), (13, (12,3)), (14, (16,4)),
        (15, (15,4)), (16, (10,4)), (17, (4,4)),
        # scheme 3
        (18, (2,4)),  (19, (2,3)), (20, (0,2)), (21, (1,2)), (22, (0,1)), (23, (1,1)),
        (24, (5,2)),  (25, (1,0)), (26, (5,1))
        
    ]
    
    for tst in tests:
        order, expected = tst
        
        asteroids = build_asteroid_map(data)
        shot_asteroids = shoot_asteroids(asteroids, center)
        res = shot_asteroids[order]

        if res.position == expected:
            print(f"SUCCESS: Got {res} as expected")
        else:
            print(f"FAILED: Expected {expected} but got {res}")

def run_day_10_2():
    """
    Q: The Elves are placing bets on which will be the 200th asteroid to be vaporized.
    Win the bet by determining which asteroid that will be; what do you get if you
    multiply its X coordinate by 100 and then add its Y coordinate?
    (For example, 8,2 becomes 802.)
    """

    print("=== Day 10 part 2 ===")
    
    data = read_from_file("input.txt")
    expected = 305

    asteroids = build_asteroid_map(data)
    center = (19,14)
    shot_asteroids = shoot_asteroids(asteroids, center)

    ast = shot_asteroids[199]
    res = ast.x * 100 + ast.y
    print(f"Answer: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

if __name__ == '__main__':
    run_tests_10_1()
    run_day_10_1()

    run_tests_10_2()
    run_day_10_2()
