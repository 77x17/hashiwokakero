class Renderer:
    def __init__(self, puzzle, bridges):
        self.grid = [[str(c) if c > 0 else "0" for c in row] for row in puzzle.grid]
        self.bridges = bridges

    def draw(self):
        for br in self.bridges:
            r1, c1 = br.a
            r2, c2 = br.b

            if br.horizontal():
                for c in range(min(c1, c2) + 1, max(c1, c2)):
                    self.grid[r1][c] = "=" if br.k == 2 else "-"
            else:
                for r in range(min(r1, r2) + 1, max(r1, r2)):
                    self.grid[r][c1] = "$" if br.k == 2 else "|"

    def print(self):
        for row in self.grid:
            print("[ " + " , ".join(f"\"{x}\"" for x in row) + " ]")

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            for row in self.grid:
                f.write("[ " + " , ".join(f"\"{x}\"" for x in row) + " ]\n")
