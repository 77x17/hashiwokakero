class Bridge:
    def __init__(self, a, b, k):
        self.a = a
        self.b = b
        self.k = k  # 1 or 2

    def horizontal(self):
        return self.a[0] == self.b[0]

    def vertical(self):
        return self.a[1] == self.b[1]

    def __repr__(self):
        return f"Bridge({self.a} -> {self.b}, {self.k})"
