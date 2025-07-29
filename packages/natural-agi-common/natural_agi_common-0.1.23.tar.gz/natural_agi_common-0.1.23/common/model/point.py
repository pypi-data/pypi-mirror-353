from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    id: str
    x: float
    y: float
    
    @classmethod
    def from_node_data(cls, node_data: dict) -> "Point":
        return cls(
            x=node_data["x"],
            y=node_data["y"],
            id=node_data["id"],
        )

    def __hash__(self):
        return hash(self.id)


@dataclass
class CornerPoint(Point):
    angle: float
    line1: str
    line2: str


@dataclass
class IntersectionPoint(Point):
    lines: List[str]


@dataclass
class EndPoint(Point):
    line: str


@dataclass
class StartPoint(Point):
    line: str
