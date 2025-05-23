class frozendict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))