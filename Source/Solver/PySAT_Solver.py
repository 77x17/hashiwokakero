import time
from pysat.solvers import Glucose3
from collections import defaultdict
from Core.Bridge import Bridge # Giữ nguyên import của bạn

class PySATSolver:
    def __init__(self, puzzle, cnf, var_map):
        self.puzzle = puzzle
        self.cnf = cnf
        self.var_map = var_map
        # Re-build mapping ngược để tìm biến Exist nhanh hơn
        self.exist_map = {}
        for name, vid in var_map.items():
            if name.startswith("Exist_"):
                # Parse name: Exist_(r1, c1)_(r2, c2)
                try:
                    content = name[6:] # Bỏ Exist_
                    split_idx = content.find(")_(")
                    if split_idx != -1:
                        s1 = content[:split_idx+1]
                        s2 = content[split_idx+2:]
                        u = eval(s1)
                        v = eval(s2)
                        self.exist_map[tuple(sorted((u, v)))] = vid
                except: pass

    def solve(self):
        solver = Glucose3(bootstrap_with=self.cnf)
        print("\n[PySAT] Solving (Iterative Mode)...")

        start_time = time.perf_counter()
        
        islands = list(self.puzzle.islands.keys())
        if not islands: return None

        final_model = None
        attempt_count = 0

        # VÒNG LẶP KIỂM TRA LIÊN THÔNG
        while solver.solve():
            attempt_count += 1
            model = set(solver.get_model())
            
            # 1. Dựng đồ thị từ nghiệm hiện tại
            adj = defaultdict(list)
            for (u, v), vid in self.exist_map.items():
                if vid in model:
                    adj[u].append(v)
                    adj[v].append(u)
            
            # 2. DFS kiểm tra liên thông
            visited = set()
            stack = [islands[0]]
            visited.add(islands[0])
            while stack:
                curr = stack.pop()
                for nxt in adj[curr]:
                    if nxt not in visited:
                        visited.add(nxt)
                        stack.append(nxt)
            
            # 3. Nếu ĐÃ liên thông -> Xong!
            if len(visited) == len(islands):
                final_model = model
                break
            
            # 4. Nếu CHƯA liên thông -> Thêm luật cấm và giải tiếp
            # Tìm "Cut": Các cạnh nối từ nhóm Visited sang nhóm Unvisited
            # Bắt buộc nghiệm tiếp theo phải có ít nhất 1 cạnh nối 2 vùng này
            cut_clause = []
            unvisited = [i for i in islands if i not in visited]
            
            for u in visited:
                for v in unvisited:
                    # Kiểm tra xem u và v có thể nối nhau không (có trong danh sách biến không)
                    pair = tuple(sorted((u, v)))
                    if pair in self.exist_map:
                        # Thêm biến Exist của cạnh này vào mệnh đề OR
                        cut_clause.append(self.exist_map[pair])
            
            if not cut_clause:
                # Đồ thị bị ngắt đôi mà không có đường nào nối được -> Vô nghiệm
                break
                
            solver.add_clause(cut_clause)
            # print(f"  Attempt {attempt_count}: Disconnected. Added cut constraint.")

        elapsed = (time.perf_counter() - start_time) * 1000
        solver.delete()

        if final_model is None:
            print("[PySAT] UNSAT")
            return None

        print(f"[PySAT] SAT solution found (Attempts: {attempt_count})")
        
        # Trích xuất kết quả Bridges
        bridges = []
        for name, var in self.var_map.items():
            if var in final_model and "Bridge_from" in name and "_with_" in name:
                # Parse lại tên biến bridge
                # Ex: Bridge_from_(0, 0)_to_(0, 2)_with_2_connect(s)
                try:
                    parts = name.split("_")
                    # Tìm index của "with" để parse chính xác
                    idx_with = parts.index("with")
                    k = int(parts[idx_with + 1])
                    
                    if k > 0:
                        # Reconstruct coords (hơi thủ công do chuỗi phức tạp)
                        # Cách nhanh hơn: Lấy từ cache nếu lưu, hoặc parse chuỗi
                        # Giả sử format chuẩn từ CNFGenerator
                        s_from = name.split("_to_")[0].replace("Bridge_from_", "")
                        s_to_raw = name.split("_to_")[1]
                        s_to = s_to_raw[:s_to_raw.find("_with_")]
                        
                        a = eval(s_from)
                        b = eval(s_to)
                        bridges.append(Bridge(a, b, k))
                except: continue

        return {
            "bridges": bridges,
            "time_ms": elapsed,
            "variables": len(self.var_map),
            "clauses": len(self.cnf.clauses)
        }
