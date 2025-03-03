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
    TENTH = 10
    ELEVENTH = 11

    COLORS = ['black', 'light slate gray', 'steel blue',
              'cyan', 'green yellow', 'hot pink',
              'NavajoWhite4', 'SlateBlue1', 'SeaGreen1',
              'DarkOliveGreen1', 'goldenrod2', 'red3',]

    def next(self):
        self.COLORS: Enum
        return ConnectionType((self.value + 1) % len(self.COLORS.value))
