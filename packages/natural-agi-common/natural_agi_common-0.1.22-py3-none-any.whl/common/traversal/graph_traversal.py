from typing import Generator, Any, Tuple, Optional
import networkx as nx

from model.point import Point
from model.vector import Vector, HorizontalDirection, VerticalDirection


class GraphTraversal:
    def __init__(self, graph: nx.Graph):
        self.graph = graph

    def calculate_direction(
        self, x1: float, y1: float, x2: float, y2: float
    ) -> Tuple[HorizontalDirection, VerticalDirection]:
        """
        Calculate the horizontal and vertical direction of movement from point (x1, y1) to (x2, y2).

        Args:
            x1 (float): X-coordinate of the start point
            y1 (float): Y-coordinate of the start point
            x2 (float): X-coordinate of the end point
            y2 (float): Y-coordinate of the end point

        Returns:
            Tuple[HorizontalDirection, VerticalDirection]: The horizontal and vertical directions
        """
        # Calculate horizontal direction
        if x2 > x1:
            h_direction = HorizontalDirection.RIGHT
        elif x2 < x1:
            h_direction = HorizontalDirection.LEFT
        else:
            h_direction = HorizontalDirection.NONE

        # Calculate vertical direction
        if y2 > y1:
            v_direction = (
                VerticalDirection.BOTTOM
            )  # In image coordinates, y increases downward
        elif y2 < y1:
            v_direction = VerticalDirection.TOP
        else:
            v_direction = VerticalDirection.NONE

        return h_direction, v_direction

    def dfs_traversal(
        self, start_node: Any
    ) -> Generator[Tuple[Point, Optional[Vector]], None, None]:
        for edge in nx.dfs_edges(self.graph, start_node):
            source_node, target_node = edge

            # Convert to your Point and Vector objects
            source_data = self.graph.nodes[source_node]
            target_data = self.graph.nodes[target_node]

            point = None
            vector = None

            if self._is_point(source_data):
                point = Point.from_node_data(source_data)
            elif self._is_vector(source_data):
                vector = Vector.from_node_data(source_data)

            if self._is_point(target_data):
                point = Point.from_node_data(target_data)
            elif self._is_vector(target_data):
                vector = Vector.from_node_data(target_data)

            if point is None and vector is None:
                raise ValueError(f"Invalid node data: {source_data} or {target_data}")

            if vector is not None:
                h_direction, v_direction = self.calculate_direction(
                    vector.x1, vector.y1, vector.x2, vector.y2
                )
                vector.horizontal_direction = h_direction
                vector.vertical_direction = v_direction

            yield point, vector

    def _is_vector(self, node_data: dict) -> bool:
        return "Vector" in node_data["labels"]

    def _is_point(self, node_data: dict) -> bool:
        return "Point" in node_data["labels"]
