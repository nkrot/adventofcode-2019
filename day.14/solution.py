#!/usr/bin/env python

import re
import numpy as np
import pandas as pd
import math

pd.set_option('display.max_columns', 500)

class NanoFactory(object):

    @classmethod
    def parse_reaction(cls, line):
        """
        NOTE: assuming that the output is a sole complex

        >>> NanoFactory.parse_reaction("7 A, 1 C => 1 D")
        [(-7, 'A'), (-1, 'C'), (1, 'D')]
        """

        complexes = re.findall(r'(\d+)\s+([A-Z]+)', line)
        def conv(cx, pos):
            n = int(cx[0])
            if pos+1 < len(complexes):
                n *= -1
            return (n, cx[1])
        complexes = [conv(cx, idx) for idx,cx in enumerate(complexes)]
        return complexes
        
    @classmethod
    def from_text(cls, text):
        if isinstance(text, type([])):
            reactions = [cls.parse_reaction(line) for line in text]
        else:
            raise ValueError(f"Can not process argument of type {type(text)}")

        return cls(reactions)

    def __init__(self, reactions=None):
        self.reactions = reactions
        self.matrix = None
        self._build_stoichiometric_matrix()
        
        self.base_substance = None
        self.product_substance = None
        self.solver = None

        self.verbose = False

    def _build_stoichiometric_matrix(self):
        if len(self.reactions) > 0:
            row_names = []
            for reaction in self.reactions:
                for cx in reaction:
                    if cx[1] not in row_names:
                        row_names.append(cx[1])
            col_names = [f"R{idx}" for idx,r in enumerate(self.reactions)]
            zeros = np.zeros((len(row_names), len(col_names)), dtype=np.int64)
    
            self.matrix = pd.DataFrame(data=zeros, columns=col_names, index=row_names)

            for idx,reaction in enumerate(self.reactions):
                col = f"R{idx}"
                for cx in reaction:
                    row = cx[1]
                    self.matrix.loc[row,col] = cx[0]

    def balance_stoichiometry(self):
        if self.solver is None:
            self.solver = StoichiometryBalanceSolver(self.matrix, self.product_substance)
            self.solver.verbose = self.verbose

        self.solver.execute()

        if self.verbose:
            print("--- Stoichiometry Matrix, balanced state ---")
            print(self.solver.solution)
            print("-"*80)

    @property
    def amount_of_base_substance(self):
        return abs(self.solver.amount_of(self.base_substance))

    @property
    def amount_of_product_substance(self):
        return abs(self.solver.amount_of(self.product_substance))

    def amount_of_product_from_amount_of_base(self, amount_base_target):
        self.balance_stoichiometry()

        amount_base_per_1_product = self.amount_of_base_substance
        amount_base = amount_base_per_1_product
        
        while amount_base < amount_base_target:
            amount_product = self.amount_of_product_substance
            incr = abs(amount_base_target // amount_base)
            if incr > 1:
                amount_product_target = amount_product * incr
            else:
                incr = (amount_base_target - amount_base) // amount_base_per_1_product
                if incr == 0:
                    break
                amount_product_target += incr
                
            # print(f"Setting target: {amount_base} -> {amount_product}; {amount_product_target}")
            self.solver.set_target(amount_product_target)
        
            # print("--- Stoichiometry Matrix, target set ---")
            # print(solver.solution)
            # print("-"*80)

            self.solver.execute()
            amount_base = self.amount_of_base_substance

        return self.amount_of_product_substance
        
class StoichiometryBalanceSolver(object):
    def __init__(self, matrix, prod):
        self.initial = matrix
        self.product_name = prod
        self.verbose = False
        self.solution = None

        # compute coordinates of the cell that contains amount of product
        row = self.initial.loc[self.product_name]
        self.product_reaction_name = row[row > 0].index[0]

    def execute(self):
        self._vprint(f"Solving for {self.product_name}")
        if self.solution is None:
            self.solution = self.initial.copy()

        n = 0 
        while True:
            n += 1
            assert n < 1000, "Infinite loop?"
            substance, amount = self.find_deficit()
            if not substance:
                break
            self.fix_deficit(substance, amount)
            
        return self.solution

    def set_target(self, target_amount):
        self._vprint(f"Setting target: ({self.product_name}, {target_amount})")
        current_amount = self.solution.loc[self.product_name, self.product_reaction_name]
        self.fix_deficit(self.product_name, current_amount-target_amount)
        
    def fix_deficit(self, substance, amount):
        self._vprint(f"Fixing deficit of {(substance, amount)}")
        amount = abs(amount)
        
        row = self.initial.loc[substance]
        col = row[row > 0].index[0]
        output = self.initial.loc[substance, col]

        self._vprint(f"REACTION:\n{self.initial[col]}\n/REACTION")
        incr = int(math.ceil(amount / output))
        self._vprint(f"Need to add {incr} of the above reaction")
        self.solution[col] += self.initial[col] * incr
        self._vprint(f"INCREASED:\n{self.solution[col]}\n")
        
    def find_deficit(self):
        """
        TODO: can be improved by selecting a better candidate
        """
        res = (None, None)

        sums = self.solution.sum(axis=1)
        sums = sums.loc[~sums.index.isin(['ORE', self.product_name])]
        deficits = sums[sums < 0]
        self._vprint(f"DEFICITS:\n{deficits}\n/DEFICITS")
    
        if not deficits.empty:
            substance = deficits.index[0]
            res = (substance, deficits.loc[substance])

        self._vprint(f"DEFICIT: {res}")

        return res

    def amount_of(self, substance):
        """
        Get total amount of substance across all reactions.
        The result is returned with the same sign as in the matrix.
        """
        return self.solution.sum(axis=1).loc[substance]
        
    def _vprint(self, msg):
        if self.verbose:
            print(msg)

################################################################################

def read_lines_from_file(fname):
    with open(fname) as fd:
        lines = [line.strip() for line in fd.readlines()]
    return lines

################################################################################

tests = [
    ( ["10 ORE => 10 A",
       "1 ORE => 1 B",
       "7 A, 1 B => 1 C",
       "7 A, 1 C => 1 D",
       "7 A, 1 D => 1 E",
       "7 A, 1 E => 1 FUEL"
    ], 31, None),
        
    ( ["9 ORE => 2 A",
       "8 ORE => 3 B",
       "7 ORE => 5 C",
       "3 A, 4 B => 1 AB",
       "5 B, 7 C => 1 BC",
       "4 C, 1 A => 1 CA",
       "2 AB, 3 BC, 4 CA => 1 FUEL"
    ], 165, None),
        
    ( ["157 ORE => 5 NZVS", 
       "165 ORE => 6 DCFZ",
       "44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL",
       "12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ",
       "179 ORE => 7 PSHF",
       "177 ORE => 5 HKGWZ",
       "7 DCFZ, 7 PSHF => 2 XJWVT",
       "165 ORE => 2 GPVTF",
       "3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT"
    ],
      13312,   # part 1: min amount of ORE required for 1 FUEL
      82892753 # part 2: max amount of fuel that can be produced with 1 trillion ORE
    ),
        
    ( ["2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG",
       "17 NVRVD, 3 JNWZP => 8 VPVL",
       "53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL",
       "22 VJHF, 37 MNCFX => 5 FWMGM",
       "139 ORE => 4 NVRVD",
       "144 ORE => 7 JNWZP",
       "5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC",
       "5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV",
       "145 ORE => 6 MNCFX",
       "1 NVRVD => 8 CXFTF",
       "1 VJHF, 6 MNCFX => 4 RFSQX",
       "176 ORE => 6 VJHF"
    ], 180697, 5586022 ),

    ( ["171 ORE => 8 CNZTR",
       "7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL",
       "114 ORE => 4 BHXH",
       "14 VRPVC => 6 BMBT",
       "6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL",
       "6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT",
       "15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW",
       "13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW",
       "5 BMBT => 4 WPTQ",
       "189 ORE => 9 KTJDG",
       "1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP",
       "12 VRPVC, 27 CNZTR => 2 XDBXC",
       "15 KTJDG, 12 BHXH => 5 XCVML",
       "3 BHXH, 2 VRPVC => 7 MZWV",
       "121 ORE => 7 VRPVC",
       "7 XCVML => 6 RJRHP",
       "5 BHXH, 4 VRPVC => 5 LTCX",
    ], 2210736, 460664)
]

def run_tests_14_1():
    print("=== Day 14 part 1 (tests) ===")

    verbose = False

    for tst in tests:
        lines, expected, _ = tst

        nf = NanoFactory.from_text(lines)
        nf.base_substance = 'ORE'
        nf.product_substance = 'FUEL'

        if verbose:
            for r in nf.reactions:
                print(r)
            print("--- Stoichiometry Matrix, initial state ---")
            print(nf.matrix)
            print("-"*80)

        nf.balance_stoichiometry()

        if verbose:
            print("--- Stoichiometry Matrix, final state ---")
            print(nf.solver.solution)
            print("-"*80)

        res = nf.amount_of_base_substance
        print(f"Answer: minimum amount of {nf.base_substance} required to produce 1 {nf.product_substance}: {res}")

        if res == expected:
            print(f"SUCCESS: Got {res} as expected")
        else:
            print(f"FAILED: Expected {expected} but got {res}")

def run_day_14_1():
    """
    Given the list of reactions in your puzzle input, what is the minimum amount
    of ORE required to produce exactly 1 FUEL?
    """

    print("=== Day 14 part 1 ===")
    
    lines = read_lines_from_file("input.14.txt")
    expected = 346961

    verbose = False
    
    nf = NanoFactory.from_text(lines)
    nf.base_substance = 'ORE'
    nf.product_substance = 'FUEL'

    if verbose:
        for r in nf.reactions:
            print(r)
        print("--- Stoichiometry Matrix, initial state ---")
        print(nf.matrix)
        print("-"*80)

    nf.balance_stoichiometry()
    
    if verbose:
        print("--- Stoichiometry Matrix, final state ---")
        print(nf.solver.solution)
        print("-"*80)

    res = nf.amount_of_base_substance
    print(f"Answer: minimum amount of {nf.base_substance} required to produce 1 {nf.product_substance}: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def run_tests_14_2():
    """
    Given 1 trillion ORE, what is the maximum amount of FUEL you can produce?
    1 trillion = 1 000 000 000 000
    """

    print("=== Day 14 part 2 (tests) ===")

    verbose = False
    available_amount_of_base_substance = 1000000000000

    for tst in tests:
        lines, _, expected = tst
        if expected is None:
            continue

        nf = NanoFactory.from_text(lines)
        nf.base_substance = 'ORE'
        nf.product_substance = 'FUEL'
    
        if verbose:
            for r in nf.reactions:
                print(r)
            print("--- Stoichiometry Matrix, initial state ---")
            print(nf.matrix)
            print("-"*80)

        nf.amount_of_product_from_amount_of_base(available_amount_of_base_substance)

        if verbose:
            print("--- Stoichiometry Matrix, final state with new target ---")
            print(nf.solver.solution)
            print("-"*80)

        # amount_base = abs(solver.amount_of(base_substance))
        # print(f"Amount of base substance ({base_substance}): {amount_base}")
        # print(f"Underused: {amount_base_target - amount_base}")
        
        res = nf.amount_of_product_substance
        print(f"Answer: amount of {nf.product_substance} from {available_amount_of_base_substance} of {nf.base_substance}: {res}")

        if res == expected:
            print(f"SUCCESS: Got {res} as expected")
        else:
            print(f"FAILED: Expected {expected} but got {res} (mismatch: {expected - res})")

def run_day_14_2():
    """
    Given 1 trillion ORE, what is the maximum amount of FUEL you can produce?
    1 trillion = 1 000 000 000 000
    """

    print("=== Day 14 part 2 ===")

    lines = read_lines_from_file("input.14.txt")
    expected = 4065790
    available_amount_of_base_substance = 1000000000000

    verbose = False
    
    nf = NanoFactory.from_text(lines)
    nf.base_substance = 'ORE'
    nf.product_substance = 'FUEL'

    if verbose:
        for r in nf.reactions:
            print(r)
        print("--- Stoichiometry Matrix, initial state ---")
        print(nf.matrix)
        print("-"*80)

    nf.amount_of_product_from_amount_of_base(available_amount_of_base_substance)
    
    if verbose:
        print("--- Stoichiometry Matrix, final state ---")
        print(nf.solver.solution)
        print("-"*80)

    res = nf.amount_of_product_substance
    print(f"Answer: amount of {nf.product_substance} from {available_amount_of_base_substance} of {nf.base_substance}: {res}")

    if res == expected:
        print(f"SUCCESS: Got {res} as expected")
    else:
        print(f"FAILED: Expected {expected} but got {res}")

def nice_to_learn():
    print("--- using chempy ---")
    from chempy import Substance
    from chempy import balance_stoichiometry
    from pprint import pprint
    
    # substances = {s.name: s for s in [
    #     Substance('pancake',     composition={'eggs': 1, 'spoons_of_flour': 2, 'cups_of_milk': 1}),
    #     Substance('eggs_6pack',  composition={'eggs': 6}),
    #     Substance('milk_carton', composition={'cups_of_milk': 4}),
    #     Substance('flour_bag',   composition={'spoons_of_flour': 60})
    # ]}
    # for x in balance_stoichiometry({'eggs_6pack', 'milk_carton', 'flour_bag'},
    #                                {'pancake'}, substances=substances):
    #     pprint(dict(x))


    substances = {s.name: s for s in [
        Substance('ORE',  composition={} ),
        Substance('AIR',  composition={} ),
        Substance('A',    composition={'ORE': 1, 'AIR': 1} ),
        Substance('B',    composition={'ORE': 1, 'AIR': 1} ),
        Substance('C',    composition={'A': 7, 'B': 1}),
        Substance('D',    composition={'A': 7, 'C': 1}),
        Substance('E',    composition={'A': 7, 'D': 1}),
        Substance('FUEL', composition={'A': 7, 'E': 1})
    ]}

    for x in balance_stoichiometry({'ORE', 'A',  'B',  'C', 'D', 'E'},
                                   {'FUEL': 1}, substances=substances, underdetermined=None):
        pprint(dict(x))

if __name__ == '__main__':
    run_tests_14_1() # ok
    run_day_14_1()   # ok

    run_tests_14_2() # ok
    run_day_14_2()   # ok
