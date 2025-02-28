from enum import Enum


class ConnectionType(Enum):
    GENERIC = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3

    COLORS = ['black', 'magenta', 'cyan', 'firebrick1']

    def next(self):
        return ConnectionType((self.value + 1) % 4)
