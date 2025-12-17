import time
from pysat.solvers import Glucose3
from Core.Bridge import Bridge

class PySATSolver:
    def __init__(self, puzzle, cnf, var_map):
        self.puzzle = puzzle
        self.cnf = cnf
        self.var_map = var_map

    def solve(self):
        solver = Glucose3()

        for clause in self.cnf:
            solver.add_clause(clause)

        print("\n[PySAT] Solving...")

        start_time = time.perf_counter()
        sat = solver.solve()
        elapsed = (time.perf_counter() - start_time) * 1000

        if not sat:
            print("[PySAT] UNSAT")
            return None

        model = set(solver.get_model())
        print("[PySAT] SAT solution found")

        bridges = []

        for name, var in self.var_map.items():
            if var in model and "with_" in name:
                parts = name.split("_")
                a = eval(parts[2])
                b = eval(parts[4])
                k = int(parts[6])
                if k > 0:
                    bridges.append(Bridge(a, b, k))

        return {
            "bridges": bridges,
            "time_ms": elapsed,
            "variables": len(self.var_map),
            "clauses": len(self.cnf.clauses)
        }
