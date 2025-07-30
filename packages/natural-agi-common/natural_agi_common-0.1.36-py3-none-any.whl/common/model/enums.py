from enum import Enum


class ContourType(Enum):
    CLOSED = "Closed"
    OPEN = "Open"


class ContourDevelopment(Enum):
    MONOTONIC = "Monotonic"
    NON_MONOTONIC = "Non-monotonic"
    UNKNOWN = "Unknown"


class HorizontalDirection(Enum):
    LEFT = "Left"
    RIGHT = "Right"
    NONE = "None"


class VerticalDirection(Enum):
    TOP = "Top"
    BOTTOM = "Bottom"
    NONE = "None"
