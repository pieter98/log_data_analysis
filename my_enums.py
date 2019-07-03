from enum import Enum
from enum import IntEnum


class WorkshopType(Enum):
    CREATE = 0
    FIX = 1
    GENERATED = 2
    GENERATED2 = 3
    RECORDED = 4
    BOTH = 5

class FunctionalDataset(IntEnum):
    GENERATED1 = 0
    GENERATED2 = 1
    REAL1 = 2
    GENERATED3 = 3
    GENERATED4 = 4
    RECORDED = 5
    GENERATED5 = 6
