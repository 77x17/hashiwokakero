from CNF.Parser import Puzzle
from CNF.CNF_Generator import CNFGenerator
from Solver.AStar_Solver import AStarSolver
from Solver.PySAT_Solver import PySATSolver
from Solver.Backtracking_Solver import BacktrackingSolver
from Solver.BruteForce_Solver import BruteForceSolver
from Core.Renderer import Renderer
from Core.Bridge import Bridge
import os
import time
# Import thư viện Timeout
from func_timeout import func_timeout, FunctionTimedOut

# Cấu hình thời gian tối đa cho mỗi thuật toán (tính bằng giây)
TIMEOUT_SECONDS = 30 

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

def run_astar(puzzle, filename):
    print("\n" + "="*20 + " RUNNING A-STAR " + "="*20)
    
    try:
        solver = AStarSolver(puzzle, bridge_candidates(puzzle))
        
        # func_timeout(số_giây, tên_hàm)
        result = func_timeout(TIMEOUT_SECONDS, solver.solve)
        
    except FunctionTimedOut:
        print(f"[A*] TIMEOUT!")
        return
    
    # Kiểm tra xem có tìm thấy lời giải không
    if result is None or result.get("bridges") is None:
        print("A* did not find a solution.")
        return
    
    bridges = [Bridge(a, b, k) for (a, b), k in result["bridges"].items() if k > 0]

    renderer = Renderer(puzzle, bridges)
    renderer.draw()

    print("\n[A* OUTPUT]\n")
    renderer.print()

    print("\n[A* STATS]")
    print(f"Expanded states : {result['expanded']}")
    print(f"Time (ms)       : {result['time_ms']:.2f}")
    print(f"Total bridges   : {sum(result['bridges'].values())}")

    out = f"Outputs/AStar/{filename}"
    os.makedirs("Outputs/AStar", exist_ok=True)
    renderer.save(out)

def run_pysat(puzzle, filename):
    print("\n" + "="*20 + " RUNNING PYSAT " + "="*20)
    
    try:
        gen = CNFGenerator(puzzle)
        cnf, var_map = gen.generate()
        solver = PySATSolver(puzzle, cnf, var_map)
        
        # --- BỌC TIMEOUT ---
        result = func_timeout(TIMEOUT_SECONDS, solver.solve)
        
    except FunctionTimedOut:
        print(f"[PySAT] TIMEOUT!")
        return

    # Kiểm tra result cho PySAT
    if result is None or result.get("bridges") is None:
        print("PySAT did not find a solution.")
        return
        
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

    out = f"Outputs/PySAT/{filename}"
    os.makedirs("Outputs/PySAT", exist_ok=True)
    renderer.save(out)
    
def run_backtracking(puzzle, filename):
    print("\n" + "="*20 + " RUNNING BACKTRACKING " + "="*20)
    
    try:
        candidates = bridge_candidates(puzzle)
        solver = BacktrackingSolver(puzzle, candidates)
        
        # --- BỌC TIMEOUT ---
        result = func_timeout(TIMEOUT_SECONDS, solver.solve)
        
    except FunctionTimedOut:
        print(f"[Backtracking] TIMEOUT!")
        return

    if result is None or result.get("bridges") is None:
        print("Backtracking did not find a solution.")
        return

    # Chuyển đổi kết quả dictionary sang List[Bridge] để vẽ
    bridges = [Bridge(a, b, k) for (a, b), k in result["bridges"].items() if k > 0]

    renderer = Renderer(puzzle, bridges)
    renderer.draw()

    print("\n[Backtracking OUTPUT]")
    renderer.print()

    print("\n[Backtracking STATS]")
    print(f"Recursion calls : {result['expanded']}") # Số lần gọi hàm đệ quy
    print(f"Time (ms)       : {result['time_ms']:.2f}")
    print(f"Total bridges   : {sum(result['bridges'].values())}")

    out = f"Outputs/Backtracking/{filename}"
    os.makedirs("Outputs/Backtracking", exist_ok=True)
    renderer.save(out)
    print(f"Saved result to: {out}")
    
def run_bruteforce(puzzle, filename):
    print("\n" + "="*20 + " RUNNING BRUTE FORCE " + "="*20)
    try:
        candidates = bridge_candidates(puzzle)
        solver = BruteForceSolver(puzzle, candidates)
        
        # Bọc Timeout
        result = func_timeout(TIMEOUT_SECONDS, solver.solve)
        
    except FunctionTimedOut:
        print(f"[BruteForce] TIMEOUT!")
        return

    if result is None or result.get("bridges") is None:
        print("BruteForce did not find a solution.")
        return
    
    # Chuyển đổi kết quả dictionary sang List[Bridge] để vẽ
    bridges = [Bridge(a, b, k) for (a, b), k in result["bridges"].items() if k > 0]
    renderer = Renderer(puzzle, bridges)
    renderer.draw()

    print("\n[Backtracking OUTPUT]")
    renderer.print()

    print("\n[Backtracking STATS]")
    print(f"Expanded nodes  : {result['expanded']}") # Số lần gọi hàm đệ quy
    print(f"Time (ms)       : {result['time_ms']:.2f}")
    print(f"Total bridges   : {sum(result['bridges'].values())}")

    out = f"Outputs/Backtracking/{filename}"
    os.makedirs("Outputs/Backtracking", exist_ok=True)
    renderer.save(out)
    print(f"Saved result to: {out}")

if __name__ == "__main__":
    for i in range(1, 11):
        # Tạo tên file input và output
        input_file = f"input-{i:02d}.txt"
        output_file = f"output-{i:02d}.txt"
        
        input_path = f"Inputs/{input_file}"
        
        # Kiểm tra nếu file không tồn tại thì bỏ qua để tránh lỗi crash
        if not os.path.exists(input_path):
            print(f"\n File {input_path} not exist. Ignore.")
            continue
        
        print(f"\n{'=' * 60}")
        print(f" Processing File: {input_file} ".center(60, '#'))
        print(f"{'='*60}")
        
        try:
            puzzle = Puzzle.from_file(input_path)

            # Truyền thêm tham số output_file vào các hàm
            run_astar(puzzle, output_file)
            run_pysat(puzzle, output_file)
            run_backtracking(puzzle, output_file)
            run_bruteforce(puzzle, output_file)

        except Exception as e:
            print(f" Error while running the file {input_file}: {e}")