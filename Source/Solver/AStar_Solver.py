import heapq
import time
from collections import defaultdict, deque

# ==========================================
# 1. Các hàm hình học (Helper Functions)
# ==========================================
def get_segment(u, v):
    """Trả về tọa độ đoạn thẳng chuẩn hóa (x1 < x2 hoặc y1 < y2)"""
    r1, c1 = u
    r2, c2 = v
    if r1 > r2 or (r1 == r2 and c1 > c2):
        return (r2, c2, r1, c1)
    return (r1, c1, r2, c2)

def check_cross(seg1, seg2):
    """Kiểm tra 2 đoạn thẳng có cắt nhau không (chỉ xét vuông góc)"""
    r1, c1, r2, c2 = seg1  # Segment 1
    r3, c3, r4, c4 = seg2  # Segment 2

    # Song song hoặc trùng nhau -> Không cắt (trong logic Hashi đã lọc trùng từ trước)
    if (r1 == r2 and r3 == r4) or (c1 == c2 and c3 == c4):
        return False

    # Seg1 Ngang, Seg2 Dọc
    if r1 == r2 and c3 == c4:
        return (min(c1, c2) < c3 < max(c1, c2)) and (min(r3, r4) < r1 < max(r3, r4))
    
    # Seg1 Dọc, Seg2 Ngang
    if c1 == c2 and r3 == r4:
        return (min(c3, c4) < c1 < max(c3, c4)) and (min(r1, r2) < r3 < max(r1, r2))
    
    return False

# ==========================================
# 2. Class State (Trạng thái)
# ==========================================
class State:
    def __init__(self, idx, remain, bridges, g=0):
        self.idx = idx          # Chỉ số của cạnh đang xét trong danh sách candidates
        self.remain = remain    # Tuple: dung lượng còn lại của các đảo (immutable để hash)
        self.bridges = bridges  # Tuple: các cầu đã xây ((u, v), k)
        self.g = g              # Chi phí (số cầu đã xây)

    # Heuristic: Tổng số chân cầu còn thiếu
    def h(self):
        return sum(self.remain)

    def f(self):
        return self.g + self.h()

    # Để so sánh trong Priority Queue
    def __lt__(self, other):
        return self.f() < other.f()
    
    # Để lưu vào Closed Set (Tránh lặp)
    # Key bao gồm: Đã xét đến cạnh nào, tình trạng các đảo, các cầu đã xây
    def key(self):
        return (self.idx, self.remain)

# ==========================================
# 3. Class AStarSolver
# ==========================================
class AStarSolver:
    def __init__(self, puzzle, candidates):
        self.puzzle = puzzle
        # Sorted để đảm bảo thứ tự duyệt cố định (Deterministic)
        self.candidates = sorted(candidates, key=lambda x: (x[0], x[1]))
        self.islands_order = list(puzzle.islands.keys()) # Map index -> coord
        self.coord_to_idx = {coord: i for i, coord in enumerate(self.islands_order)}
        
        # Precompute: Xung đột cắt nhau
        self.conflicts = defaultdict(list)
        self.precompute_conflicts()

    def precompute_conflicts(self):
        """Tạo bản đồ xung đột: Cạnh i cắt những cạnh j nào?"""
        segments = [get_segment(u, v) for u, v in self.candidates]
        n = len(self.candidates)
        for i in range(n):
            for j in range(i + 1, n):
                if check_cross(segments[i], segments[j]):
                    self.conflicts[i].append(j)
                    self.conflicts[j].append(i)

    def check_subtour_and_connectivity(self, current_bridges_dict, remain_dict):
        """
        Kiểm tra 2 điều kiện quan trọng:
        1. Đảo đầy (remain=0) có bị cô lập không?
        2. Nhóm đảo đầy có tạo thành subtour (chu trình kín nhỏ) không?
        """
        # Dựng đồ thị hiện tại
        adj = defaultdict(list)
        active_nodes = set()
        for (u, v), k in current_bridges_dict.items():
            if k > 0:
                adj[u].append(v)
                adj[v].append(u)
                active_nodes.add(u)
                active_nodes.add(v)

        # 1. Quick Check: Đảo đã full (remain=0) nhưng degree=0 -> SAI
        for coord, rem in remain_dict.items():
            if rem == 0 and coord not in active_nodes:
                return False # Đảo cô lập

        # 2. Subtour Elimination (Quan trọng cho tính đúng đắn)
        # Tìm các thành phần liên thông (Connected Components)
        visited = set()
        total_islands = len(self.puzzle.islands)
        
        for start_node in active_nodes:
            if start_node in visited:
                continue
            
            # BFS tìm component
            component = set()
            q = deque([start_node])
            visited.add(start_node)
            component.add(start_node)
            
            while q:
                u = q.popleft()
                for v in adj[u]:
                    if v not in visited:
                        visited.add(v)
                        component.add(v)
                        q.append(v)
            
            # Kiểm tra trạng thái component
            # Nếu TẤT CẢ các đảo trong component đều đã FULL (remain=0)
            # Thì component này đã "đóng băng", không thể nối thêm ra ngoài.
            is_closed_component = all(remain_dict[node] == 0 for node in component)
            
            if is_closed_component:
                # Nếu đóng băng mà không chứa hết tất cả các đảo -> Subtour (SAI)
                if len(component) < total_islands:
                    return False

        # Nếu đã đi hết danh sách cạnh (goal check), bắt buộc phải liên thông toàn bộ
        # Hàm is_goal sẽ gọi lại check này, ở đây ta chỉ prune nhánh sai.
        return True

    def solve(self):
        start_time = time.perf_counter()
        
        # Trạng thái ban đầu: chưa xét cạnh nào (idx=-1), remain đầy đủ
        initial_remain = tuple(self.puzzle.islands[coord] for coord in self.islands_order)
        start_state = State(0, initial_remain, (), 0)
        
        open_list = [(start_state.f(), start_state)]
        closed = set()
        expanded = 0

        print(f"\n[A*] Solving Sequential (Total candidates: {len(self.candidates)})...")

        while open_list:
            _, cur = heapq.heappop(open_list)

            # Goal Check: Đã xét hết các cạnh và Remain tất cả bằng 0
            if cur.idx >= len(self.candidates):
                if all(r == 0 for r in cur.remain):
                    # Kiểm tra liên thông lần cuối
                    bridges_dict = dict(cur.bridges)
                    if self.check_subtour_and_connectivity(bridges_dict, 
                                      {self.islands_order[i]: r for i, r in enumerate(cur.remain)}):
                        
                        elapsed = (time.perf_counter() - start_time) * 1000
                        print(f"[A*] Solution found. Expanded: {expanded}")
                        return {
                            "bridges": bridges_dict,
                            "time_ms": elapsed,
                            "expanded": expanded
                        }
                continue # Không đạt goal thì bỏ qua (Backtrack implicitly)

            # Kiểm tra Closed Set
            state_key = cur.key()
            if state_key in closed:
                continue
            closed.add(state_key)
            expanded += 1

            # --- TRANSITION: Rẽ nhánh tại cạnh candidates[cur.idx] ---
            # Chúng ta quyết định xây 0, 1 hay 2 cầu tại cạnh này
            u, v = self.candidates[cur.idx]
            u_idx = self.coord_to_idx[u]
            v_idx = self.coord_to_idx[v]
            
            # Lấy thông tin hiện tại
            bridges_map = dict(cur.bridges)
            
            # Kiểm tra xung đột với các cầu đã xây trước đó
            # Nếu cạnh này bị cắt bởi một cạnh đã xây -> Chỉ được xây 0 cầu
            is_blocked = False
            for conflict_idx in self.conflicts[cur.idx]:
                # Do chúng ta duyệt tuần tự idx tăng dần, chỉ cần check các idx < cur.idx
                # Tuy nhiên trong map `bridges`, ta cần tìm xem cạnh conflict_idx có tồn tại không
                # Cách đơn giản: Duyệt qua bridges hiện tại xem có cái nào nằm trong list conflict không
                # (Vì bridges lưu ((u,v), k), hơi khó map ngược về idx.
                #  Tốt nhất là check geometry lại hoặc lưu idx vào bridge)
                pass 
                # Tạm thời để đơn giản và chính xác, ta check blocked bằng danh sách conflict đã precompute
                # Ta cần biết trong cur.bridges có cạnh nào thuộc self.conflicts[cur.idx] không
                # Để tối ưu, ta có thể không cần check ở đây nếu ta đảm bảo logic bên dưới.
            
            # Optimization: Check conflict nhanh
            # Tìm tất cả các cạnh đã xây (k > 0)
            built_edges_indices = set() 
            # (Phần này nếu làm kỹ cần lưu idx vào state để check O(1), 
            #  nhưng với Hashi thường số cầu ít nên check O(N) vẫn ổn)
            
            # --- Nhánh 1: Không xây cầu (k=0) ---
            # Luôn luôn khả thi
            heapq.heappush(open_list, (cur.f(), State(cur.idx + 1, cur.remain, cur.bridges, cur.g)))

            # --- Nhánh 2 & 3: Xây 1 hoặc 2 cầu (k=1, 2) ---
            # Điều kiện 1: Đảo u và v còn đủ chỗ
            rem_u = cur.remain[u_idx]
            rem_v = cur.remain[v_idx]

            # Kiểm tra xem cạnh này có bị cắt bởi cầu đã xây không
            # Lấy list index các cạnh xung đột
            conflicting_indices = self.conflicts[cur.idx]
            # Kiểm tra trong cur.bridges (dạng ((coord, coord), k)) có cái nào khớp với index không?
            # Cách này chậm. 
            # -> Cách nhanh: Check trực tiếp geometry với các cầu đã có trong bridges
            cross_detected = False
            current_seg = get_segment(u, v)
            for (bu, bv), bk in cur.bridges:
                if bk > 0:
                    if check_cross(current_seg, get_segment(bu, bv)):
                        cross_detected = True
                        break
            
            if not cross_detected:
                for k in [1, 2]:
                    if rem_u >= k and rem_v >= k:
                        # Tạo state mới
                        new_remain_list = list(cur.remain)
                        new_remain_list[u_idx] -= k
                        new_remain_list[v_idx] -= k
                        new_remain = tuple(new_remain_list)
                        
                        new_bridges = cur.bridges + (( (u, v), k ),)
                        
                        # --- QUAN TRỌNG: Pruning (Cắt tỉa) ---
                        # Kiểm tra xem việc xây cầu này (hoặc làm đầy đảo) có tạo ra subtour chết không
                        # Logic: Nếu đảo u hoặc v về 0, chạy check connectivity
                        temp_bridges_dict = dict(new_bridges)
                        temp_remain_dict = {self.islands_order[i]: r for i, r in enumerate(new_remain)}
                        
                        if (new_remain_list[u_idx] == 0 or new_remain_list[v_idx] == 0):
                            if not self.check_subtour_and_connectivity(temp_bridges_dict, temp_remain_dict):
                                continue # Subtour detected -> Bỏ qua nhánh này
                        
                        # Nếu qua được các bài test -> Thêm vào queue
                        new_state = State(cur.idx + 1, new_remain, new_bridges, cur.g + k)
                        heapq.heappush(open_list, (new_state.f(), new_state))

        elapsed = (time.perf_counter() - start_time) * 1000
        print("[A*] No solution found / Queue empty")
        return None