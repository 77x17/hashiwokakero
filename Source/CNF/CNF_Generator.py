from pysat.formula import CNF
from itertools import combinations, product

class CNFGenerator:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.cnf = CNF()
        self.var_map = {}
        self.counter = 1
        # Lưu mapping trực tiếp để truy cập nhanh từ Solver
        self.exist_vars = {} 

    def new_var(self, name):
        if name not in self.var_map:
            self.var_map[name] = self.counter
            self.counter += 1
        return self.var_map[name]

    def bridge_var(self, a, b, k):
        return self.new_var(f"Bridge_from_{a}_to_{b}_with_{k}_connect(s)")

    def valid_pair(self, a, b):
        """Kiểm tra 2 đảo có thể kết nối thẳng hàng không"""
        r1, c1 = a; r2, c2 = b
        if r1 == r2:
            for c in range(min(c1, c2) + 1, max(c1, c2)):
                if self.puzzle.grid[r1][c] != 0: return False
            return True
        if c1 == c2:
            for r in range(min(r1, r2) + 1, max(r1, r2)):
                if self.puzzle.grid[r][c1] != 0: return False
            return True
        return False

    def orientation(self, a, b):
        if a[0] == b[0]: return "H"
        if a[1] == b[1]: return "V"
        return None

    def bridge_cells(self, a, b):
        r1, c1 = a; r2, c2 = b
        cells = set()
        if r1 == r2:
            for c in range(min(c1, c2) + 1, max(c1, c2)): cells.add((r1, c))
        elif c1 == c2:
            for r in range(min(r1, r2) + 1, max(r1, r2)): cells.add((r, c1))
        return cells

    def generate(self):
        islands = list(self.puzzle.islands.keys())
        self.bridge_vars_cache = {} 

        # 1. Tạo biến cầu và ràng buộc cơ bản
        for a, b in combinations(islands, 2):
            if not self.valid_pair(a, b): continue

            v1 = self.bridge_var(a, b, 1)
            v2 = self.bridge_var(a, b, 2)
            
            self.bridge_vars_cache[(a, b)] = (v1, v2)


            # Tạo biến Exist đại diện cho việc "Có cầu nối giữa a và b"
            # Biến này rất quan trọng để check liên thông sau này
            exist = self.new_var(f"Exist_{a}_{b}")
            self.exist_vars[(a, b)] = exist
            self.exist_vars[(b, a)] = exist # Lưu cả 2 chiều để dễ tìm

            # Exist <-> (v1 OR v2)
            self.cnf.append([-exist, v1, v2])
            self.cnf.append([-v1, exist])
            self.cnf.append([-v2, exist])
            self.cnf.append([-v1, -v2])

        # 2. Ràng buộc số lượng cầu tại mỗi đảo (Degree)
        for island, need in self.puzzle.islands.items():
            related = []
            for (a, b), (v1, v2) in self.bridge_vars_cache.items():
                if island == a or island == b:
                    related.append((1, v1)) # v1 trọng số 1
                    related.append((2, v2)) # v2 trọng số 2
            self.encode_sum_equals(related, need)

        # 3. Ràng buộc không cắt nhau
        self.add_no_crossing_constraints()

        # LƯU Ý: Đã bỏ phần check liên thông tĩnh (Flow/Tarjan) ở đây
        # Để Solver tự xử lý bằng vòng lặp
        
        return self.cnf, self.var_map

    def encode_sum_equals(self, vars_k, total):
        n = len(vars_k)
        # Brute-force tổ hợp (An toàn vì số lượng hướng <= 4)
        for comb in product([0, 1], repeat=n):
            s = sum(comb[i] * vars_k[i][0] for i in range(n))
            if s != total:
                clause = []
                for i, val in enumerate(comb):
                    clause.append(-vars_k[i][1] if val else vars_k[i][1])
                self.cnf.append(clause)

    def add_no_crossing_constraints(self):
        bridges = []
        # Gom các cạnh tiềm năng
        processed = set()
        for (a, b), _ in self.bridge_vars_cache.items():
            pair = tuple(sorted((a, b)))
            if pair in processed: continue
            processed.add(pair)
            
            # Lấy biến Exist
            exist_id = self.exist_vars.get((a, b))
            if exist_id:
                bridges.append((exist_id, self.orientation(a, b), self.bridge_cells(a, b)))

        # Check cắt nhau đôi một
        for i in range(len(bridges)):
            v1, o1, c1 = bridges[i]
            for j in range(i + 1, len(bridges)):
                v2, o2, c2 = bridges[j]
                if o1 != o2 and not c1.isdisjoint(c2):
                    self.cnf.append([-v1, -v2])
