from enum import Enum


class ConnectionType(Enum):
    GENERIC = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7
    EIGHTH = 8
    NINTH = 9

    COLORS = ['black', 'magenta', 'cyan',
              'firebrick1', 'gold2', 'RoyalBlue1',
              'lime green', 'spring green', 'light slate blue']

    def next(self):
        return ConnectionType((self.value + 1) % 9)
