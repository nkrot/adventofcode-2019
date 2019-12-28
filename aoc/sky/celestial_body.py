#
# TODO
# Previous implementation are in day 6 and day 10
# At least day 10 can be refactored to use this class
# field .id was renamed to .name

import re
import math
import json

class CelestialBody(object):

    @classmethod
    def from_text(cls, line, name=None):
        # day.12
        m = re.search('<x=(-?\d+), y=(-?\d+), z=(-?\d+)>', line)
        if m:
            x = int(m.group(1))
            y = int(m.group(2))
            z = int(m.group(3))
            body = cls(x, y, z)
            if name:
                body.name = name
            return body
        else:
            raise ValueError(f"Unrecognized serialization format: {line}")

    # TODO: move to sky.physics
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

    # TODO: move to sky.physics
    @classmethod
    def distance_between(self, a, b):
        return math.sqrt((a.x - b.x)**2 + (a.y-b.y)**2 + (a.z-b.z)**2)

    # TODO: move to sky.physics
    # (day.10 only)
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

    def __init__(self, x, y, z=0, name=None):
        self.x = x
        self.y = y
        self.z = z
        self.name = name
        self.distance = None   # distance to origin
        self.declension = None # w.r.t. origin
        self.skyquarter = None # in what Sky quarter is the object located
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.period = None

    @property
    def position(self):
        return (self.x, self.y, self.z)

    def update_position(self):
        """
        Update position from velocity
        """
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        return self.position
        
    @property
    def velocity(self):
        return (self.vx, self.vy, self.vz)

    def update_velocity(self, update):
        assert len(update) == len(self.velocity), "Wrong size of update vector"
        self.vx += update[0]
        self.vy += update[1]
        self.vz += update[2]
        return self.velocity
        
    def __iter__(self):
        # TODO: get rid of it
        return iter(self.position)

    def __str__(self):
        #fields = ["name", "declension", "skyquarter", "distance"] # day.10
        fields = ["position", "velocity", "period", "name"] # day.12
        data = { f:getattr(self, f) for f in fields }
        return json.dumps(data)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {str(self)}>"

    def is_at(self, position):
        if isinstance(position, type(self)):
            position = coord.position
        return self.position == position

    def potential_energy(self):
        return sum([abs(c) for c in self.position])

    def kinetic_energy(self):
        return sum([abs(v) for v in self.velocity])

    def energy(self):
        return self.potential_energy() * self.kinetic_energy()

    def __eq__(self, other):
        """
        [day.12]
        """
        fields = ["name", "position", "velocity"]
        return all(getattr(self, att) == getattr(other, att) for att in fields)
    
