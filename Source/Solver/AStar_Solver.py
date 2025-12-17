import heapq
import time

class State:
    def __init__(self, remain, bridges, g=0):
        self.remain = remain
        self.bridges = bridges
        self.g = g

    def h(self):
        return sum(self.remain.values())

    def f(self):
        return self.g + self.h()

    def is_goal(self):
        return all(v == 0 for v in self.remain.values())

    def key(self):
        return (
            tuple(sorted(self.remain.items())),
            tuple(sorted(self.bridges.items()))
        )

    def __lt__(self, other):
        return self.f() < other.f()


class AStarSolver:
    def __init__(self, puzzle, candidates):
        self.puzzle = puzzle
        self.candidates = candidates

    def successors(self, state):
        next_states = []

        for (a, b) in self.candidates:
            cur_k = state.bridges.get((a, b), 0)

            for k in (1, 2):
                if cur_k + k > 2:
                    continue
                if state.remain[a] < k or state.remain[b] < k:
                    continue

                new_remain = dict(state.remain)
                new_remain[a] -= k
                new_remain[b] -= k

                new_bridges = dict(state.bridges)
                new_bridges[(a, b)] = cur_k + k

                next_states.append(State(new_remain, new_bridges, state.g + k))

        return next_states

    def solve(self):
        start_time = time.perf_counter()

        start = State(dict(self.puzzle.islands), {}, 0)
        open_list = [(start.f(), start)]
        closed = set()

        expanded = 0

        print("\n[A*] Solving...")

        while open_list:
            _, cur = heapq.heappop(open_list)

            if cur.key() in closed:
                continue

            closed.add(cur.key())
            expanded += 1

            if cur.is_goal():
                elapsed = (time.perf_counter() - start_time) * 1000
                print("[A*] Solution found")

                return {
                    "bridges": cur.bridges,
                    "expanded": expanded,
                    "time_ms": elapsed
                }

            for nxt in self.successors(cur):
                if nxt.key() not in closed:
                    heapq.heappush(open_list, (nxt.f(), nxt))

        elapsed = (time.perf_counter() - start_time) * 1000
        print("[A*] No solution")

        return {
            "bridges": None,
            "expanded": expanded,
            "time_ms": elapsed
        }

