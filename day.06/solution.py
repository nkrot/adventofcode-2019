#!/usr/bin/env python

# # #
# TODO: what is the opposite of satellite? namely, the term for an object
# around which another object is orbiting
# TODO: study yield in Python, implement dfs
# how to implement any function that requires dfs using one generic dfs traversal
# and a function (visitor). Plus that function may need to access variables
# that exist in the object being visited.
# TODO: need a better visualisation of planet alone, like 'B', and
#       a planet-orbiting-another planet, like 'A)B'

class OrbitMap(object):
    
    def __init__(self):
        self.bodies = {}
        self.com = None # Center of Mass object

    def find(self, obj):
        name = obj if isinstance(obj, str) else obj.name
        finds = list(filter(lambda b: b.name == name, self.bodies.values()))
        return finds[0] if len(finds) > 0 else None
            
    def find_or_create(self, name):
        if name not in self.bodies:
            self.bodies[name] = CelestialBody(name)

        return self.bodies[name]

    def build_map(self, sky_object_pairs):
        """
        """
        for pair in sky_object_pairs:
            m, sat = pair.split(')')
            
            m   = self.find_or_create(m)
            sat = self.find_or_create(sat)
            m.add_satellite(sat)
            
            if m.name == 'COM':
                m.com = True
                self.com = m

    # def dfs(self):
    #     yield(self.com)
    #     self.com.dfs()

    def set_distance_to_com(self):
        # TODO: generalize to use dfs
        self.com.distance_to_com = 0
        for sat in self.com.satellites:
            sat.set_distance_to_com()

    def path_between(self, b1, b2):
        p1 = b1.path_to_com()
        p2 = b2.path_to_com()
        
        # print(f"Paths from to COM")
        # print(p1)
        # print(p2)

        # now remove planets that are in both paths
        removed = None
        while True:
            if p1[-1] == p2[-1]:
                removed = p1.pop()
                p2.pop()
            else:
                break

        p = []
        if removed:
            # there is a path between two planets
            # readd last common planet
            p1.append(removed)
            p1.extend(reversed(p2))
            p = p1

        # print(f"Path between {b1} and {b2}: {p}")

        return p
    
    def __str__(self):
        res = []
        for name, obj in self.bodies.items():
            res.append(str(obj))
        return " ".join(res)

class CelestialBody(object):

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent # TODO: a better name
        self.satellites = []
        self.com = False # is Center of Mass
        self.distance_to_com = None

    def add_satellite(self, body):
        # TODO: avoid adding if already exists
        self.satellites.append(body)
        body.parent = self

    def set_distance_to_com(self):
        self.distance_to_com = self.parent.distance_to_com + 1
        for sat in self.satellites:
            sat.set_distance_to_com()

    # def dfs(self):
    #     # TODO: implement
    #     print(f"DFS/{self.name}")
    #     for sat in self.satellites:
    #         yield(sat)
    #         sat.dfs()

    def path_to_com(self):
        if self.com:
            return []
        else:
            return [ self.parent ] + self.parent.path_to_com()
        
    def __str__(self):
        if self.parent:
            s = f"{self.parent.name}){self.name}"
        else:
            s = f"|{self.name}"
        s += f"[{self.distance_to_com}]"
        return s

    def __repr__(self):
        return str(self)

################################################################################
# main
    
tests = [
    (["COM)B", "B)C", "C)D", "D)E", "E)F", "B)G", "G)H", "D)I", "E)J", "J)K", "K)L"],
     42, None),

    (["COM)B", "B)C", "C)D", "D)E", "E)F", "B)G", "G)H", "D)I","E)J", "J)K", "K)L", "K)YOU", "I)SAN"],
     54, 4)
    ]

def run_tests():
    for lst,exp_num_orbits,exp_num_hops in tests:
        orbit_map = OrbitMap()
        orbit_map.build_map(lst)
        orbit_map.set_distance_to_com()
        print(orbit_map)

        num_orbits = sum([body.distance_to_com for body in orbit_map.bodies.values()])
        print(f"Number of Orbits: {num_orbits}")
        
        if num_orbits == exp_num_orbits:
            print(f"SUCCESS: Got {num_orbits} as expected")
        else:
            print(f"FAILED: Expected {exp_num_orbits} but got {num_orbits}")
    
        you = orbit_map.find('YOU')
        santa = orbit_map.find('SAN')

        if you and santa:
            print(you)
            print(santa)
            path = orbit_map.path_between(you, santa)
            num_hops = len(path) - 1

            if num_hops == exp_num_hops:
                print(f"SUCCESS: Got {num_hops} as expected")
            else:
                print(f"FAILED: Expected {exp_num_hops} but got {num_hops}")
            

def read_from_file(fname):
    """
    One line only
    """
    
    with open(fname) as fd:
        lines = fd.readlines()
    lines = [ line.strip() for line in lines ]

    return lines

def run_day_6_1():
    """
    What is the total number of direct and indirect orbits in your map data?
    """
    
    print("=== Day 06, Task 1 ===")
    
    lines = read_from_file("input.txt")
    expected = 312697

    orbit_map = OrbitMap()
    orbit_map.build_map(lines)
    orbit_map.set_distance_to_com()

    num_orbits = sum([body.distance_to_com for body in orbit_map.bodies.values()])
    print(f"Number of Orbits: {num_orbits}")
        
    if num_orbits == expected:
        print(f"SUCCESS: Got {num_orbits} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {num_orbits}")
    
def run_day_6_2():
    """
    What is the minimum number of orbital transfers required to move from the object YOU
    are orbiting to the object SAN is orbiting? (Between the objects they are orbiting -
    not between YOU and SAN.)
    """
    
    print("=== Day 06, Task 2 ===")
    
    lines = read_from_file("input.txt")
    expected = 466

    orbit_map = OrbitMap()
    orbit_map.build_map(lines)

    you = orbit_map.find('YOU')
    santa = orbit_map.find('SAN')

    # print(you)
    # print(santa)
    path = orbit_map.path_between(you, santa)
    num_hops = len(path) - 1

    print(f"Number of Orbital Transfers: {num_hops}")

    if num_hops == expected:
        print(f"SUCCESS: Got {num_hops} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {num_hops}")

if __name__ == '__main__':
    run_tests()

    run_day_6_1()
    run_day_6_2()
    
