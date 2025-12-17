from pysat.formula import CNF
from itertools import combinations, product


class CNFGenerator:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.cnf = CNF()
        self.var_map = {}
        self.counter = 1

    def new_var(self, name):
        self.var_map[name] = self.counter
        self.counter += 1
        return self.var_map[name]

    def bridge_var(self, a, b, k):
        return self.new_var(
            f"Bridge_from_{a}_to_{b}_with_{k}_connect(s)"
        )

    def flow_var(self, a, b):
        return self.new_var(f"Flow_{a}_to_{b}")
    
    def valid_pair(self, a, b):
        r1, c1 = a
        r2, c2 = b

        if r1 == r2:
            for c in range(min(c1, c2) + 1, max(c1, c2)):
                if self.puzzle.grid[r1][c] != 0:
                    return False
            return True

        if c1 == c2:
            for r in range(min(r1, r2) + 1, max(r1, r2)):
                if self.puzzle.grid[r][c1] != 0:
                    return False
            return True

        return False

    def orientation(self, a, b):
        if a[0] == b[0]:
            return "H"
        if a[1] == b[1]:
            return "V"
        return None

    def bridge_cells(self, a, b):
        r1, c1 = a
        r2, c2 = b
        cells = set()

        if r1 == r2:
            for c in range(min(c1, c2) + 1, max(c1, c2)):
                cells.add((r1, c))
        elif c1 == c2:
            for r in range(min(r1, r2) + 1, max(r1, r2)):
                cells.add((r, c1))

        return cells

    def generate(self):
        islands = list(self.puzzle.islands.keys())

        self.bridge_vars = {}
        self.bridge_exist = {}
        self.flow_vars = {}

        for a, b in combinations(islands, 2):
            if not self.valid_pair(a, b):
                continue

            v0 = self.bridge_var(a, b, 0)
            v1 = self.bridge_var(a, b, 1)
            v2 = self.bridge_var(a, b, 2)

            self.bridge_vars[(a, b, 0)] = v0
            self.bridge_vars[(a, b, 1)] = v1
            self.bridge_vars[(a, b, 2)] = v2

            self.cnf.append([v0, v1, v2])
            self.cnf.append([-v0, -v1])
            self.cnf.append([-v0, -v2])
            self.cnf.append([-v1, -v2])

            exist = self.new_var(f"Exist_{a}_{b}")
            self.bridge_exist[(a, b)] = exist
            self.bridge_exist[(b, a)] = exist

            self.cnf.append([-exist, v1, v2])
            self.cnf.append([-v1, exist])
            self.cnf.append([-v2, exist])

        for island, need in self.puzzle.islands.items():
            related = []
            for (a, b, k), v in self.bridge_vars.items():
                if island in (a, b) and k > 0:
                    related.append((k, v))
            self.encode_sum_equals(related, need)

        self.add_no_crossing_constraints()

        self.add_connectivity_constraints(islands)

        return self.cnf, self.var_map

    def encode_sum_equals(self, vars_k, total):
        n = len(vars_k)
        for comb in product([0, 1], repeat=n):
            s = sum(comb[i] * vars_k[i][0] for i in range(n))
            if s != total:
                clause = []
                for i, val in enumerate(comb):
                    clause.append(-vars_k[i][1] if val else vars_k[i][1])
                self.cnf.append(clause)

    def add_no_crossing_constraints(self):
        bridges = []

        for (a, b, k), v in self.bridge_vars.items():
            if k == 0:
                continue
            bridges.append((v, self.orientation(a, b), self.bridge_cells(a, b)))

        for i in range(len(bridges)):
            v1, o1, c1 = bridges[i]
            for j in range(i + 1, len(bridges)):
                v2, o2, c2 = bridges[j]
                if o1 != o2 and c1 & c2:
                    self.cnf.append([-v1, -v2])

    def add_connectivity_constraints(self, islands):
        root = islands[0]

        for a, b in combinations(islands, 2):
            if not self.valid_pair(a, b):
                continue

            f_ab = self.flow_var(a, b)
            f_ba = self.flow_var(b, a)

            self.flow_vars[(a, b)] = f_ab
            self.flow_vars[(b, a)] = f_ba

            self.cnf.append([-f_ab, self.bridge_exist[(a, b)]])
            self.cnf.append([-f_ba, self.bridge_exist[(a, b)]])

        for v in islands:
            incoming = []
            outgoing = []

            for u in islands:
                if u == v:
                    continue
                if (u, v) in self.flow_vars:
                    incoming.append(self.flow_vars[(u, v)])
                if (v, u) in self.flow_vars:
                    outgoing.append(self.flow_vars[(v, u)])

            if v != root:
                self.cnf.append(incoming)

                for f_out in outgoing:
                    self.cnf.append([-f_out] + incoming)
