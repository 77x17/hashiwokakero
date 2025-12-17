import time
import sys

# Tăng giới hạn đệ quy
sys.setrecursionlimit(5000)

class BruteForceSolver:
    def __init__(self, puzzle, candidates):
        self.puzzle = puzzle
        self.candidates = candidates
        self.n_candidates = len(candidates)
        
        # Mảng lưu trạng thái số cầu của mỗi candidate (0, 1, 2)
        self.assignment = [0] * self.n_candidates
        
        # Dictionary lưu trữ số cầu hiện tại đang nối vào mỗi đảo
        # Để kiểm tra nhanh điều kiện capacity
        self.current_counts = {node: 0 for node in puzzle.islands}

        self.expanded = 0
        self.start_time = 0

    def _is_crossing(self, bridge1, bridge2):
        """Kiểm tra 2 cầu có cắt nhau không (Logic hình học cơ bản)"""
        (r1a, c1a), (r1b, c1b) = bridge1
        (r2a, c2a), (r2b, c2b) = bridge2

        min_r1, max_r1 = min(r1a, r1b), max(r1a, r1b)
        min_c1, max_c1 = min(c1a, c1b), max(c1a, c1b)
        min_r2, max_r2 = min(r2a, r2b), max(r2a, r2b)
        min_c2, max_c2 = min(c2a, c2b), max(c2a, c2b)

        is_horz1 = (min_r1 == max_r1)
        is_vert2 = (min_c2 == max_c2)

        if is_horz1 and is_vert2:
            return (min_r2 < min_r1 < max_r2) and (min_c1 < min_c2 < max_c1)
        
        is_vert1 = (min_c1 == max_c1)
        is_horz2 = (min_r2 == max_r2)

        if is_vert1 and is_horz2:
            return (min_r1 < min_r2 < max_r1) and (min_c2 < min_c1 < max_c2)
            
        return False

    def _check_valid_move(self, idx, k):
        """Kiểm tra xem gán k cầu vào candidate[idx] có hợp lệ ngay lúc này không"""
        u, v = self.candidates[idx]

        # 1. Kiểm tra sức chứa (Capacity Check)
        # Nếu cộng thêm k mà vượt quá số ghi trên đảo -> Sai
        if self.current_counts[u] + k > self.puzzle.islands[u]:
            return False
        if self.current_counts[v] + k > self.puzzle.islands[v]:
            return False

        # 2. Kiểm tra cắt nhau (Crossing Check) - Duyệt trâu
        # So sánh cầu hiện tại với TẤT CẢ các cầu đã xây trước đó
        if k > 0:
            for prev_idx in range(idx):
                if self.assignment[prev_idx] > 0:
                    if self._is_crossing(self.candidates[idx], self.candidates[prev_idx]):
                        return False
        return True

    def _check_connectivity(self):
        """Kiểm tra tính liên thông toàn bản đồ (BFS/DFS)"""
        adj = {node: [] for node in self.puzzle.islands}
        active_bridges = 0
        
        for i, k in enumerate(self.assignment):
            if k > 0:
                u, v = self.candidates[i]
                adj[u].append(v)
                adj[v].append(u)
                active_bridges += 1
        
        if active_bridges == 0 and len(self.puzzle.islands) > 1:
            return False

        start_node = next(iter(adj))
        visited = set([start_node])
        queue = [start_node]
        
        while queue:
            curr = queue.pop(0)
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return len(visited) == len(self.puzzle.islands)

    def _solve_recursive(self, idx):
        self.expanded += 1

        # --- BASE CASE: Đã duyệt hết tất cả candidates ---
        if idx == self.n_candidates:
            # Kiểm tra xem TẤT CẢ các đảo đã ĐỦ số lượng chưa (Exact Match)
            for node, required in self.puzzle.islands.items():
                if self.current_counts[node] != required:
                    return False
            
            # Kiểm tra liên thông
            if not self._check_connectivity():
                return False
                
            return True

        # --- RECURSIVE STEP ---
        u, v = self.candidates[idx]

        # Thử lần lượt các giá trị: 0, 1, 2
        # (Brute force thường thử từ 0 lên, hoặc 2 xuống đều được)
        for k in [0, 1, 2]:
            if self._check_valid_move(idx, k):
                # Apply move
                self.assignment[idx] = k
                self.current_counts[u] += k
                self.current_counts[v] += k

                # Recurse
                if self._solve_recursive(idx + 1):
                    return True

                # Backtrack (Undo move)
                self.current_counts[u] -= k
                self.current_counts[v] -= k
                self.assignment[idx] = 0
        
        return False

    def solve(self):
        print("\n[BruteForce] Solving...")
        self.start_time = time.perf_counter()
        
        success = self._solve_recursive(0)
        
        elapsed = (time.perf_counter() - self.start_time) * 1000

        if success:
            print("[BruteForce] Solution found")
            result_bridges = {}
            for i, k in enumerate(self.assignment):
                if k > 0:
                    result_bridges[self.candidates[i]] = k
            
            return {
                "bridges": result_bridges,
                "expanded": self.expanded,
                "time_ms": elapsed
            }
        else:
            print("[BruteForce] No solution")
            return {
                "bridges": None,
                "expanded": self.expanded,
                "time_ms": elapsed
            }