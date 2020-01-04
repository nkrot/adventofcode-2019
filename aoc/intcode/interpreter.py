#
# TODO
# 1. day 11 may have broken solutions to 5,7,9 (recursion has been removed).
# 2. can yield be used in do_output to imitate switching?

import sys
from .tape import Tape

class Interpreter(object):
    opcodes = [1,2,3,4,5,6,7,8,99]

    def __init__(self, tape, inputs=None, outputs=None):
        self.tape = Tape(tape) if isinstance(tape, str) else tape
        self.verbose = False
        self.result = None
        self.inputs = inputs
        self.outputs = outputs
        self.param_modes = []
        self.relative_base = 0
        self.running = 0  # (-1,0,1) (halt,idle,running)
        self.device_id = None
        self.status = "IDLE"
        self.uplink = None

    def execute(self):
        """
        >>> ii = Interpreter("1,5,6,0,99,10,20")
        >>> ii.execute()
        30
        >>> str(ii.tape)
        '30,5,6,0,99,10,20'

        >>> tape = Tape("1,0,0,0,99")
        >>> ii = Interpreter(tape)
        >>> ii.execute()
        2

        >>> tape = Tape("1,0,0,0,99")
        >>> tape.patch((2,1))
        >>> ii = Interpreter(tape)
        >>> ii.execute()
        3

        >>> tape = Tape("1,9,10,3,2,3,11,0,99,30,40,50")
        >>> ii = Interpreter(tape)
        >>> ii.execute()
        3500

        >>> ii = Interpreter("3,0,4,0,99", inputs=[20])
        >>> ii.execute()
        20
        20

        >>> ii = Interpreter("1002,4,3,4,33")
        >>> ii.execute()
        1002

        # ifeq, positional
        >>> ii = Interpreter("3,9,8,9,10,9,4,9,99,-1,8", inputs=[8])
        >>> _ = ii.execute()
        1

        # ifeq, positional
        >>> ii = Interpreter("3,9,8,9,10,9,4,9,99,-1,8", inputs=[7])
        >>> _ = ii.execute()
        0

        # ifeq, immediate
        >>> ii = Interpreter("3,3,1108,-1,8,3,4,3,99", inputs=[8])
        >>> _ = ii.execute()
        1

        # jump-if-false, positional
        >>> ii = Interpreter("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9", inputs=[0])
        >>> _ = ii.execute()
        0

        # jump, positional
        >>> ii = Interpreter("3,3,1105,-1,9,1101,0,0,12,4,12,99,1", inputs=[10])
        >>> _ = ii.execute()
        1

        >>> s = "3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99"
        >>> ii = Interpreter(s, inputs=[7])
        >>> _ = ii.execute()
        999
        >>> ii = Interpreter(s, inputs=[8])
        >>> _ = ii.execute()
        1000
        >>> ii = Interpreter(s, inputs=[9])
        >>> _ = ii.execute()
        1001

        >>> s = "3,11,9,13,2001,11,8,12,4,12,99,0,10,4"
        >>> ii = Interpreter(s, inputs=[5])
        >>> _ = ii.execute()
        15

        >>> s = "109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99"
        >>> ii = Interpreter(s)
        >>> _ = ii.execute() # doctest:+ELLIPSIS
        109
        ...

        """

        if self.running == 0:
            self.running = 1
            self.status = "STARTING"
            self.tape.rewind()
            self._vprint(f"TAPE: {self.tape}")

        elif self.running >= 1:
            self.status = "RESUMING"

        elif self.running == -1:
            return self.result

        self._vprint(f"{self._about()} is {self.status} inputs={self.inputs}")

        while self.running == 1:
            code = self.read_opcode()

            if   code == 99: self.do_halt()
            elif code ==  1: self.do_sum()
            elif code ==  2: self.do_multiply()
            elif code ==  3: self.do_read_input()
            elif code ==  4: self.do_output()
            elif code ==  5: self.do_jump_if_true()
            elif code ==  6: self.do_jump_if_false()
            elif code ==  7: self.do_iflt()
            elif code ==  8: self.do_ifeq()
            elif code ==  9: self.do_adjust_relative_base()
            else:
                raise ValueError(f"Unknown opcode {code}")

            if self.running == 2:
                # (day 11) wait for input, alternative to mutual recursion
                self.running = 1
                break

        return self.tape.at(0) # not always :(

    def _about(self):
        return f"DEVICE {self.__class__.__name__} with id={self.device_id}"

    def set_uplink_to(self, other):
        self.uplink  = other
        self.outputs = self.uplink.inputs

    def do_halt(self):
        if self.running == -1:
            return False
        self._vprint(f"ADDR={self.tape.position} HALT, result={self.result}")
        self._vprint(f"{self._about()} has become HALT")
        self.running = -1
        # not sure if it is necessary to halt connected controllers
        # if self.uplink:
        #     self.uplink.do_halt()

    @property
    def finished(self):
        """
        Return True if computer has come to a halt
        """
        return self.running == -1

    def read_opcode(self):
        del self.param_modes[:]
        code = self.tape.read()

        # handle a complex opcode that contain both the instruction and parameter
        # modes.
        if code not in self.__class__.opcodes:
            for offset in range(2, len(str(code))):
                pmode = int(code % 10**(offset+1) / 10**offset)
                self.param_modes.append(pmode)
            code = code % 100

        return code

    def do_read_input(self):
        addr = self.tape.position
        self._vprint(f"ADDR={addr}, READ-INPUT, param modes: {self.param_modes}")
        arg_1 = self.read_param(immediate=True)
        if self.inputs:
            arg_2 = self.inputs.pop(0)
        else:
            print("Please input an integer:")
            arg_2 = int(sys.stdin.readline().strip())
        self._vprint(f"ADDR={addr}, READ-INPUT, value {arg_2}, saving it at {arg_1}")
        self.tape.write_to(arg_1, arg_2)
        self._vprint(f"Tape: {self.tape}")

    def do_output(self):
        addr = self.tape.position
        arg_1 = self.read_param()
        self._vprint(f"ADDR={addr}, OUTPUT, params {(arg_1)}")
        self._vprint(f"Tape: {self.tape}")
        self.result = arg_1

        if isinstance(self.outputs, type([])):
            self.outputs.append(arg_1)
        else:
            print(arg_1)

        if self.uplink is not None:
            # works for day 7, 9 but creates deep recursion in day 11
            #self.uplink.execute()

            # introduced in day 11
            # TODO: test if it works for day 7, 9
            self.running = 2

            # TODO: can it be reused in previous days: 7,9,11,15 etc
            #yield self.outputs

    def do_adjust_relative_base(self):
        addr = self.tape.position
        arg_1 = self.read_param()
        self.relative_base += arg_1
        self._vprint(f"ADDR={addr}, ADJUST-REL-BASE, params {(arg_1)} sets relative base to {self.relative_base}")
        self._vprint(f"Tape: {self.tape}")

    def do_sum(self):
        addr = self.tape.position
        self._vprint(f"ADDR={addr}, SUM, PARAM modes: {self.param_modes}")
        arg_1 = self.read_param()
        arg_2 = self.read_param()
        arg_3 = self.read_param(immediate=True)
        val   = arg_1 + arg_2
        self._vprint(f"ADDR={addr}, SUM, params: {(arg_1, arg_2)} saving {val} at {arg_3}")
        self.tape.write_to(arg_3, val)
        self._vprint(f"Tape: {self.tape}")

    def do_multiply(self):
        addr = self.tape.position
        self._vprint(f"ADDR={addr}, MULTIPLY, PARAM modes: {self.param_modes}")
        arg_1 = self.read_param()
        arg_2 = self.read_param()
        arg_3 = self.read_param(immediate=True)
        val   = arg_1 * arg_2
        self._vprint(f"ADDR={addr}, MULTIPLY, params: {(arg_1, arg_2)} saving {val} at {arg_3}")
        self.tape.write_to(arg_3, val)
        self._vprint(f"Tape: {self.tape}")

    def do_iflt(self):
        addr = self.tape.position
        arg_1 = self.read_param()
        arg_2 = self.read_param()
        arg_3 = self.read_param(immediate=True)
        val = 1 if arg_1 < arg_2 else 0
        self._vprint(f"ADDR={addr}, IFLT, params: {(arg_1, arg_2)} saving {val} at {arg_3}")
        self.tape.write_to(arg_3, val)
        self._vprint(f"Tape: {self.tape}")

    def do_ifeq(self):
        addr = self.tape.position
        arg_1 = self.read_param()
        arg_2 = self.read_param()
        arg_3 = self.read_param(immediate=True)
        val = 1 if arg_1 == arg_2 else 0
        self._vprint(f"ADDR={addr}, IFEQ, params: {(arg_1, arg_2)} saving {val} at {arg_3}")
        self.tape.write_to(arg_3, val)
        self._vprint(f"Tape: {self.tape}")

    def do_jump_if_true(self):
        """
        If the first parameter is non-zero, it sets the instruction
        pointer to the value from the second parameter. Otherwise, it does nothing.
        """
        addr = self.tape.position
        arg_1 = self.read_param()
        arg_2 = self.read_param()
        action = "stay"
        if arg_1 != 0:
            self.tape.rewind(arg_2)
            action = f"jump to {arg_2}"
        self._vprint(f"ADDR={addr}, JUMP-IF-TRUE, params: {(arg_1, arg_2)} {action}")
        self._vprint(f"Tape: {self.tape}")

    def do_jump_if_false(self):
        """
        if the first parameter is zero, it sets the instruction pointer to the value
        from the second parameter. Otherwise, it does nothing.
        """
        addr = self.tape.position
        arg_1 = self.read_param()
        arg_2 = self.read_param()
        action = "stay"
        if arg_1 == 0:
            self.tape.rewind(arg_2)
            action = f"jump to {arg_2}"
        self._vprint(f"ADDR={addr}, JUMP-IF-FALSE, params: {(arg_1, arg_2)} {action}")
        self._vprint(f"Tape: {self.tape}")

    def read_param(self, immediate=False):
        """
        Reads from the tape and returns one parameter.
        Reading algorithm is determined by the parameter mode <pmode>
          0 -- positional mode: the value is an address of the actual value
          1 -- immediate mode: the value is the actual value
          2 -- relative mode, is like positional but the value is the offset that,
               when combined with relative base, becomes the value
        Providing immediate=True forces the value to NOT be interpretet as address
        but rather the value itself. In other words, it forbids the interpretation
        of the value in the positional mode.
        """
        addr = self.tape.position
        self._vprint(f"ADDR={addr}, READ-PARAM, param modes: {self.param_modes}")

        val   = self.tape.read()
        pmode = self.pop_param_mode(0)

        if pmode == 2:
            val += self.relative_base

        if immediate or pmode == 1:
            pass
        else:
            val = self.tape.at(val)

        self._vprint(f"ADDR={addr}, READ-PARAM, value to return: {val}")

        return val

    def pop_param_mode(self, otherwise):
        """
        Retrieves next parameter mode, if available, otherwise returns provided
        value <otherwise>.

        Watch out: once the value was retrieved, it is deleted from the list of
        parameter modes. Therefore, it should be used only once for each parameter.
        """

        if len(self.param_modes) > 0:
            return self.param_modes.pop(0)

        return otherwise

    def _vprint(self, msg):
        if self.verbose:
            print(f"  {msg}", file=sys.stderr)
