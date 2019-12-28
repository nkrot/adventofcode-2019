"""
A collection of methods for computing physical properties of celestial objects
and mutual effects.
"""

def gravity_between(body_1, body_2):
    """
    Compute gravity effect between given given two Celestial Bodies. 

    On each axis (x, y, and z), the velocity of each moon changes by exactly +1 or -1
    to pull the moons together. For example, 
      if Ganymede has an x position of 3, and 
         Callisto has a x position of 5, 
      then 
         Ganymede's x velocity changes by +1 (because 5 > 3) and 
         Callisto's x velocity changes by -1 (because 3 < 5).
    However, if the positions on a given axis are the same, the velocity on that axis
    does not change for that pair of moons.

    Returns
    -------
    a pair (tuple) of tuples, each describing the effect of gravity on the other body

    >>> a = (3,2,1)
    >>> b = (3,2,1)
    >>> gravity_between(a, b)
    ((0, 0, 0), (0, 0, 0))

    >>> ganymede = (3,2,1)
    >>> callisto = (5,5,1)
    >>> gravity_between(ganymede, callisto)
    ((-1, -1, 0), (1, 1, 0))

    """

    body_1 = getattr(body_1, "position", body_1)
    body_2 = getattr(body_2, "position", body_2)

    assert len(body_1) == len(body_2), \
        f"ERROR: Size does not match {len(body_1)} vs {len(body_2)}"
    
    diffs = [c1-c2 for c1,c2 in zip(body_1, body_2)]
    
    gravity_1on2 = [0 if d == 0 else int(d/abs(d)) for d in diffs]
    gravity_2on1 = [-1 * d for d in gravity_1on2]

    gravity_1on2 = tuple(gravity_1on2)
    gravity_2on1 = tuple(gravity_2on1)

    return (gravity_1on2, gravity_2on1)

def gravity_from(body, others):
    """
    Compute how much gravity given <body> receives from other bodies in <others>

    >>> a = (3,2,1)
    >>> b = (5,5,1)
    >>> c = (3,2,1)
    >>> d = (0,2,10)
    >>> gravity_from(a, [b, c])
    (1, 1, 0)
    >>> gravity_from(a, [a, b, c])
    (1, 1, 0)
    >>> gravity_from(a, [a])
    (0, 0, 0)
    >>> gravity_from(a, [d,b])
    (0, 1, 1)
    """

    gravity = [0] * len(getattr(body, "position", body))

    for other_body in others:
        _, gravity_from_other = gravity_between(body, other_body)
        gravity = [a+b for a,b in zip(gravity, gravity_from_other)]

    gravity = tuple(gravity)

    return gravity
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
