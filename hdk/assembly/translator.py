import collections


class SymbolTable(collections.UserDict):
    _predefined_symbols = {
        **{f"R{i}": i for i in range(16)},
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576,
    }

    def __init__(self):
        self._next_variable_location = 16
        super().__init__(self._predefined_symbols)

    def map_variable(self, symbol: str) -> int:
        if symbol in self.data:
            raise ValueError(f"Variable name {symbol!r} is already in use.")
        self.data[symbol] = self._next_variable_location
        self._next_variable_location += 1
        return self.data[symbol]
