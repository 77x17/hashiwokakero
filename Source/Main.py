from CNF.Parser import Puzzle
from CNF.CNF_Generator import CNFGenerator
from Solver.AStar_Solver import AStarSolver
from Solver.PySAT_Solver import PySATSolver
from Core.Renderer import Renderer
from Core.Bridge import Bridge
import os

def bridge_candidates(puzzle):
    islands = list(puzzle.islands.keys())
    res = []

    for i in range(len(islands)):
        for j in range(i + 1, len(islands)):
            a, b = islands[i], islands[j]
            r1, c1 = a
            r2, c2 = b

            if r1 == r2:
                if all(puzzle.grid[r1][c] == 0 for c in range(min(c1, c2)+1, max(c1, c2))):
                    res.append((a, b))

            elif c1 == c2:
                if all(puzzle.grid[r][c1] == 0 for r in range(min(r1, r2)+1, max(r1, r2))):
                    res.append((a, b))

    return res

def run_astar(puzzle):
    solver = AStarSolver(puzzle, bridge_candidates(puzzle))
    result = solver.solve()

    bridges = [Bridge(a, b, k) for (a, b), k in result["bridges"].items() if k > 0]

    renderer = Renderer(puzzle, bridges)
    renderer.draw()

    print("\n[A* OUTPUT]\n")
    renderer.print()

    print("\n[A* STATS]")
    print(f"Expanded states : {result['expanded']}")
    print(f"Time (ms)       : {result['time_ms']:.2f}")
    print(f"Total bridges   : {sum(result['bridges'].values())}")

    out = "Outputs/AStar/output-01.txt"
    os.makedirs("Outputs/AStar", exist_ok=True)
    renderer.save(out)

def run_pysat(puzzle):
    gen = CNFGenerator(puzzle)
    cnf, var_map = gen.generate()

    solver = PySATSolver(puzzle, cnf, var_map)
    result = solver.solve()

    renderer = Renderer(puzzle, result["bridges"])
    renderer.draw()

    print("\n[PySAT OUTPUT]\n")
    renderer.print()

    print("\n[PySAT STATS]")
    print(f"Variables       : {result['variables']}")
    print(f"Clauses         : {result['clauses']}")
    print(f"Time (ms)       : {result['time_ms']:.2f}")
    total = sum(br.k for br in result["bridges"])
    print(f"Total bridges   : {total}")

    out = "Outputs/PySAT/output-01.txt"
    os.makedirs("Outputs/PySAT", exist_ok=True)
    renderer.save(out)

if __name__ == "__main__":
    puzzle = Puzzle.from_file("Inputs/input-01.txt")

    run_astar(puzzle)
    run_pysat(puzzle)
