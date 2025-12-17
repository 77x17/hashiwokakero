from Core.Bridge import Bridge

class SolutionDecoder:
    def __init__(self, var_map):
        self.rev = {v:k for k,v in var_map.items()}

    def decode(self, model):
        bridges = []
        for v in model:
            if v > 0 and v in self.rev:
                name = self.rev[v]
                if "with_1_connect" in name or "with_2_connect" in name:
                    parts = name.split("_")
                    a = eval(parts[2])
                    b = eval(parts[4])
                    k = int(parts[6])
                    bridges.append(Bridge(a,b,k))
        return bridges
