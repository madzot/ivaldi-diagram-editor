from enum import Enum


class WireType(Enum):
    GENERIC = ()
    FIRST = (5, 1)
    SECOND = (5, 2, 2, 2)
    THIRD = (255, 50)
