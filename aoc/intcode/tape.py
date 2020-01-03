
import sys

class Tape(object):
    """
    >>> prg = "1,0,0,3,99" 
    >>> tape = Tape(prg)
    >>> tape.cells == [1, 0, 0, 3, 99]
    True
    """

    @classmethod
    def read_from_file(cls, fname):
        with open(fname) as fd:
            lines = fd.readlines()
        lines = [ line.strip() for line in lines ]
        return cls(lines[0])

    def __init__(self, s=None):
        if isinstance(s, self.__class__):
            self.cells = list(s.cells)
            self.position = s.position
        elif s is not None:
            self.cells = [int(i) for i in s.split(',')]
            self.position = 0
        else:
            self.cells = []
            self.position = 0

    def patch(self, corrections):
        """
        Correct values at the addresses #1 (noun) and #2 (verb) to be as provided
        in the list/tuple <corrections>
        """
        for pos,val in zip([1,2], corrections):
            self.cells[pos] = val

    def rewind(self, address=0):
        """
        If address is not given, position the pointer to the beginning of the tape.
        If address is a positive value, this is the address to which the pointer will
        be moved,
        If address if a negative value, this is offset on the left from to the current
        position.

        >>> t = Tape("1,2,3,4")
        >>> t.rewind()
        0
        >>> t.rewind(3)
        3
        >>> t.rewind(-2)
        1
        """

        if address < 0:
            self.position += address
        else:
            self.position = address

        return self.position

    def at(self, addr=None):
        """
        Access value at specified position or at current position if no position was
        provided explicitly.

        >>> t = Tape("1,2,3")
        >>> t.position
        0
        >>> t.at()
        1
        >>> t.at(2)
        3
        >>> t.position
        0
        """
        addr = self.position if addr is None else addr
        
        if addr < 0:
            raise ValueError(f"Attempting to read tape at negative address: {addr}")
        elif addr >= len(self.cells):
            self._extend_tape_upto_address(addr)
            
        return self.cells[addr]

    def read(self):
        """
        Read value at the current position and advance the head one step
        
        TODO: reimplement it to advance the pointer and read the value

        >>> t = Tape("1,2,3")
        >>> t.at()
        1
        >>> t.read()
        1
        >>> t.position
        1
        """

        # TODO: should raise StopIterationError when attempting to read past the end
        # of the tape
        val = self.at()
        self.position += 1
        return val

    def write_to(self, addr, value):
        """
        Store given <value> at the position specified in <address>

        >>> t = Tape("0,0,0")
        >>> for i in range(0,3): t.write_to(i, (1+i)*10)
        >>> str(t)
        '10,20,30'
        """
        if addr >= len(self.cells):
            self._extend_tape_upto_address(addr)
        
        self.cells[addr] = value

    def _extend_tape_upto_address(self, addr):
        """
        Extend the tape to accomodate given address <addr>.
        New cells carry the value of 0.
        """
        padding_length = 1 + addr - len(self.cells)
        self.cells.extend([0]*padding_length)

    def __str__(self):
        return ",".join([str(i) for i in self.cells])

    def append(self, data, converter=None):
        """
        Introduced in day 17p2
        Add to the tape new element(s).
        TODO: support adding negative values
        """
        
        if isinstance(data, type([])):
            for d in data:
                self.append(d, converter)
        else:
            _d = converter(data) if converter else data
            if isinstance(_d, int):
                self.cells.append(_d)
            else:
                raise ValueError(f"Can not add value of type {type(_d)} to the tape: {data}")

