class Puzzle:
    def __init__(self, grid):
        self.grid = grid
        self.h = len(grid)
        self.w = len(grid[0])
        self.islands = {
            (i, j): grid[i][j]
            for i in range(self.h)
            for j in range(self.w)
            if grid[i][j] > 0
        }

    @staticmethod
    def from_file(path):
        with open(path, encoding="utf-8") as f:
            grid = [[int(x.strip()) for x in line.split(",")] for line in f]
        return Puzzle(grid)
