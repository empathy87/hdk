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
        super().__init__(self._predefined_symbols)
        self._last_variable_location = 15

    def map_variable(self, symbol: str) -> int:
        if symbol in self.data:
            raise ValueError(f"Variable name {symbol!r} is already in use.")
        self._last_variable_location += 1
        self.data[symbol] = self._last_variable_location
        return self._last_variable_location
