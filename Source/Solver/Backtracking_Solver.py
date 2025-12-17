import time
import sys

# Tăng giới hạn đệ quy cho các map lớn
sys.setrecursionlimit(5000)

class BacktrackingSolver:
    def __init__(self, puzzle, candidates):
        """
        :param puzzle: Object Puzzle chứa thông tin đảo và grid.
        :param candidates: List các tuple ((r1, c1), (r2, c2)) thể hiện các cặp đảo có thể nối.
        """
        self.puzzle = puzzle
        self.candidates = candidates
        self.n_candidates = len(candidates)
        
        # State hiện tại của quá trình đệ quy
        # remain: Dict lưu trữ số cầu còn thiếu của mỗi đảo {coordinate: remaining_capacity}
        self.remain = dict(puzzle.islands)
        
        # current_bridges: Mảng lưu số lượng cầu (0, 1, 2) cho mỗi candidate tương ứng index
        self.current_bridges = [0] * self.n_candidates

        # Thống kê
        self.expanded = 0
        self.start_time = 0

        # Tối ưu: Pre-compute (tính trước) các cặp candidate kỵ nhau (cắt nhau)
        # conflict_map[i] = list các index j mà candidate i cắt candidate j
        self.conflict_map = self._build_conflict_map()

    def _is_crossing(self, bridge1, bridge2):
        """Kiểm tra 2 đoạn thẳng có cắt nhau không (Logic hình học)"""
        (r1a, c1a), (r1b, c1b) = bridge1
        (r2a, c2a), (r2b, c2b) = bridge2

        min_r1, max_r1 = min(r1a, r1b), max(r1a, r1b)
        min_c1, max_c1 = min(c1a, c1b), max(c1a, c1b)
        min_r2, max_r2 = min(r2a, r2b), max(r2a, r2b)
        min_c2, max_c2 = min(c2a, c2b), max(c2a, c2b)

        is_horz1 = (min_r1 == max_r1)
        is_vert2 = (min_c2 == max_c2)

        # Chỉ cắt nhau nếu 1 ngang - 1 dọc
        if is_horz1 and is_vert2:
            return (min_r2 < min_r1 < max_r2) and (min_c1 < min_c2 < max_c1)
        
        is_vert1 = (min_c1 == max_c1)
        is_horz2 = (min_r2 == max_r2)

        if is_vert1 and is_horz2:
            return (min_r1 < min_r2 < max_r1) and (min_c2 < min_c1 < max_c2)
            
        return False

    def _build_conflict_map(self):
        """Tạo danh sách các cạnh xung khắc để kiểm tra nhanh O(1) lúc chạy"""
        conflicts = [[] for _ in range(self.n_candidates)]
        for i in range(self.n_candidates):
            for j in range(i + 1, self.n_candidates):
                if self._is_crossing(self.candidates[i], self.candidates[j]):
                    conflicts[i].append(j)
                    conflicts[j].append(i)
        return conflicts

    def _check_connectivity(self):
        """Kiểm tra xem tất cả các đảo có nối liền thành 1 khối không (BFS)"""
        # Tạo đồ thị kề từ các cầu hiện có
        adj = {node: [] for node in self.puzzle.islands.keys()}
        
        active_bridges_count = 0
        for idx, k in enumerate(self.current_bridges):
            if k > 0:
                u, v = self.candidates[idx]
                adj[u].append(v)
                adj[v].append(u)
                active_bridges_count += 1
        
        if active_bridges_count == 0:
            return False # Không có cầu nào

        # Bắt đầu duyệt từ đảo đầu tiên
        start_node = next(iter(adj))
        visited = set()
        queue = [start_node]
        visited.add(start_node)
        
        while queue:
            curr = queue.pop(0)
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        # Nếu số lượng đảo duyệt được == tổng số đảo -> Liên thông
        return len(visited) == len(self.puzzle.islands)

    def _backtrack(self, idx):
        self.expanded += 1

        # --- BASE CASE: Đã duyệt hết danh sách candidate ---
        if idx == self.n_candidates:
            # 1. Kiểm tra tất cả đảo đã thỏa mãn số lượng chưa (remain == 0)
            if any(val != 0 for val in self.remain.values()):
                return False
            
            # 2. Kiểm tra tính liên thông (Connectivity)
            if not self._check_connectivity():
                return False
                
            return True

        # --- RECURSIVE STEP ---
        u, v = self.candidates[idx]

        # Kiểm tra nhanh: Nếu 1 trong 2 đảo đã đầy (remain=0), chỉ có thể chọn k=0
        if self.remain[u] == 0 or self.remain[v] == 0:
            possible_k = [0]
        else:
            # Heuristic: Thử giá trị lớn trước để khớp nhanh hơn (Greedy approach)
            # Hoặc thử 0 trước để sparse hơn. Ở đây thử 2, 1, 0.
            possible_k = [2, 1, 0] 

        for k in possible_k:
            # Check 1: Capacity constraints
            # Không được xây quá số lượng còn lại của đảo
            if self.remain[u] < k or self.remain[v] < k:
                continue

            # Check 2: Crossing constraints
            # Nếu xây cầu (k > 0), phải chắc chắn nó không cắt cầu nào ĐÃ XÂY trước đó
            if k > 0:
                is_crossed = False
                # Kiểm tra danh sách xung khắc đã tính trước
                for conflict_idx in self.conflict_map[idx]:
                    # Chỉ quan tâm các cạnh index < idx (các cạnh đã quyết định rồi)
                    if conflict_idx < idx and self.current_bridges[conflict_idx] > 0:
                        is_crossed = True
                        break
                if is_crossed:
                    continue

            # === ACTION ===
            self.current_bridges[idx] = k
            self.remain[u] -= k
            self.remain[v] -= k

            # === RECURSE ===
            if self._backtrack(idx + 1):
                return True # Tìm thấy lời giải, thoát ngay

            # === BACKTRACK (Hoàn tác) ===
            self.remain[u] += k
            self.remain[v] += k
            self.current_bridges[idx] = 0

        return False

    def solve(self):
        """Hàm chính để gọi từ bên ngoài"""
        print("\n[Backtracking] Solving...")
        self.start_time = time.perf_counter()
        
        success = self._backtrack(0)
        
        elapsed = (time.perf_counter() - self.start_time) * 1000

        if success:
            print("[Backtracking] Solution found")
            # Convert mảng current_bridges thành dictionary kết quả
            result_bridges = {}
            for i, k in enumerate(self.current_bridges):
                if k > 0:
                    result_bridges[self.candidates[i]] = k
            
            return {
                "bridges": result_bridges,
                "expanded": self.expanded,
                "time_ms": elapsed
            }
        else:
            print("[Backtracking] No solution found")
            return {
                "bridges": None,
                "expanded": self.expanded,
                "time_ms": elapsed
            }