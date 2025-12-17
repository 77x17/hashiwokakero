from pysat.formula import CNF
from itertools import combinations, product

class CNFGenerator:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.cnf = CNF()
        self.var_map = {}
        self.counter = 1

    def new_var(self, a, b, k):
        name = f"Bridge_from_{a}_to_{b}_with_{k}_connect(s)"
        self.var_map[name] = self.counter
        self.counter += 1
        return self.var_map[name]

    def valid_pair(self, a, b):
        r1,c1 = a
        r2,c2 = b
        if r1 == r2:
            for c in range(min(c1,c2)+1, max(c1,c2)):
                if self.puzzle.grid[r1][c] != 0:
                    return False
            return True
        if c1 == c2:
            for r in range(min(r1,r2)+1, max(r1,r2)):
                if self.puzzle.grid[r][c1] != 0:
                    return False
            return True
        return False

    def generate(self):
        self.bridge_vars = {}
        islands = list(self.puzzle.islands.keys())

        # Bridge variables
        for a,b in combinations(islands, 2):
            if self.valid_pair(a,b):
                vars_ = []
                for k in [0,1,2]:
                    v = self.new_var(a, b, k)
                    self.bridge_vars[(a,b,k)] = v
                    vars_.append(v)

                # exactly one of {0,1,2}
                self.cnf.append(vars_)
                self.cnf.append([-vars_[0], -vars_[1]])
                self.cnf.append([-vars_[0], -vars_[2]])
                self.cnf.append([-vars_[1], -vars_[2]])

        # Island degree constraints
        for island, need in self.puzzle.islands.items():
            related = []
            for (a,b,k),v in self.bridge_vars.items():
                if island in (a,b) and k > 0:
                    related.append((k, v))
            self.encode_sum_equals(related, need)

        return self.cnf, self.var_map

    def encode_sum_equals(self, vars_k, total):
        n = len(vars_k)
        for comb in product([0,1], repeat=n):
            s = sum(comb[i] * vars_k[i][0] for i in range(n))
            if s != total:
                clause = []
                for i,val in enumerate(comb):
                    clause.append(-vars_k[i][1] if val else vars_k[i][1])
                self.cnf.append(clause)
