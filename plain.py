import random
from typing import List, Tuple, Dict, Optional
from walker import Walker
from shapely.geometry import LineString, Polygon


class Plain:
    """
    A class to represent a plain where the walker moves. the plain can have obstacles, walls and magic portals
    """

    def __init__(self, obstacles: Optional[List[Tuple[float, float]]] = None,
                 magic_portals: Optional[Dict[Tuple[float, float], Tuple[float, float]]] = None,
                 walls: Optional[Dict[Tuple[int, int], Tuple[int, int]]] = None) -> None:
        self.__obstacles: List[Tuple[float, float]] = list(set(obstacles)) if obstacles else []
        self.__magic_portals: Dict[Tuple[float, float], Tuple[float, float]] = magic_portals if magic_portals else {}
        self.__walls: Dict[Tuple[float, float], Tuple[float, float]] = walls if walls else {}
        self.__magic_portals = self.filter_magic_portals()
        self.__first_move = True

    def filter_magic_portals(self) -> Dict[Tuple[float, float], Tuple[float, float]]:
        """
        returns a filtered dictionary of magic portals so that they are not in the same line as any wall or obstacle and
        they are not in the same line as any other magic portal
        :return: a dictionary of filtered magic portals
        """
        new_magic_portals = {}
        for portal in self.__magic_portals:
            if portal in self.__obstacles or self.__magic_portals[portal] in self.__obstacles:
                continue
            else:
                for wall in self.__walls:
                    if self.calculate_det(wall, self.__walls[wall], portal) == 0:
                        continue
                for other_portal in self.__magic_portals:
                    if portal == self.__magic_portals[other_portal] or portal == other_portal:
                        continue
            new_magic_portals[portal] = self.__magic_portals[portal]
        return new_magic_portals

    def get_obstacles(self) -> List[Tuple[float, float]]:
        return self.__obstacles

    def set_obstacles(self, obstacles: List[Tuple[float, float]]) -> None:
        self.__obstacles = list(set(obstacles)) if obstacles else []

    def get_walls(self) -> Dict[Tuple[float, float], Tuple[float, float]]:
        return self.__walls

    def set_walls(self, walls: Dict[Tuple[float, float], Tuple[float, float]]) -> None:
        self.__walls = walls if walls else {}

    def get_magic_portals(self) -> Dict[Tuple[float, float], Tuple[float, float]]:
        return self.__magic_portals

    def set_magic_portals(self, magic_portals: Dict[Tuple[float, float], Tuple[float, float]]) -> None:
        self.__magic_portals = magic_portals if magic_portals else {}
        self.filter_magic_portals()

    def crossed_point(self, walker: Walker, last_location: Tuple[float, float], point: Tuple[float, float]) -> bool:
        """
        Check if the walker has crossed a point on the plain
        :param walker: a walker object
        :param last_location: the last location of the walker
        :param point: the point to check if the walker has crossed
        :return: True if the walker has crossed the point, False otherwise
        """

        x1, y1 = walker.get_location()
        x2, y2 = last_location
        x3, y3 = point

        cross_product = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)

        if cross_product != 0:
            # If the cross product is not 0, point3 does not lie on the line segment
            return False

        # Check if point3 is within the bounding box defined by point1 and point2
        on_line = min(x1, x2) <= x3 <= max(x1, x2) and min(y1, y2) <= y3 <= max(y1, y2)
        return on_line

    def is_obstacle(self, walker: Walker, last_location: Tuple[float, float]) -> bool:
        """
        Check if the walker has collided with an obstacle
        :param walker: a walker object
        :param last_location: The last location of the walker
        :return: True if the walker has collided with an obstacle, False otherwise
        """
        for obstacle in self.__obstacles:
            if self.crossed_point(walker, last_location, obstacle):
                return True
        return False

    def magic_portal(self, walker: Walker, last_location: Tuple[float, float]) -> None:
        """
        Check if the walker has entered a magic portal and if yes moves it to the destination portal
        :param walker: a walker object
        :param last_location: the last location of the walker
        :return: None
        """
        for portal in self.__magic_portals:
            if self.crossed_point(walker, last_location, portal):
                destination = self.__magic_portals[portal]
                walker.set_location(destination)

    def calculate_det(self, point1: Tuple[float, float], point2: Tuple[float, float],
                      point3: Tuple[float, float]) -> float:
        "Calculate the determinant of the matrix formed by the vectors from point1 to point2 and point3"

        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = point3
        return (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)

    def are_collinear(self, p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> bool:
        "The function to check if the points are in the same line"

        poly = Polygon([p1, p2, p3])
        # Check if the area of the polygon is zero
        return poly.area == 0

    def hit_walls(self, walker: Walker, last_location: Tuple[float, float]) -> bool:
        """
        Check if the walker has collided with any wall by detecting if the movement
        from last_location to the walker's current location intersects any wall segments.

        :param walker: a Walker object, assumed to have a method get_location() that returns a tuple
        :param last_location: tuple representing the last recorded location of the walker
        :return: True if the walker intersects any wall, False otherwise
        """
        # Get the current location of the walker
        current_location = walker.get_location()

        # Create a LineString from the last location to the current location
        walker_path = LineString([last_location, current_location])

        # Check each wall to see if it intersects with the walker's path
        for (wall_start, wall_end) in self.__walls.items():
            wall_line = LineString([wall_start, wall_end])
            if walker_path.intersects(wall_line):
                if self.are_collinear(wall_start, wall_end, (0, 0)) and self.__first_move:
                    pass
                else:
                    return True
        return False

    def move_walker(self, walker: Walker) -> None:
        """
        Move a walker and check for obstacles, walls and magic portals
        :param walker: the walker to move
        :return: None
        """
        last_location = walker.get_location()
        reset = walker.move()
        if reset:
            self.__first_move = True # Reset the first move flag because he returned to origin
            walker.add_to_history((0,0))
            return
        else:
            if self.is_obstacle(walker, last_location) or self.hit_walls(walker, last_location):
                # If collided with an obstacle or a wall, take the walker back to its last location
                walker.set_location(last_location)
                return
            # Check for magic portal
            self.magic_portal(walker, last_location)
            walker.add_to_history(walker.get_location())
            if self.__first_move:
                self.__first_move = False


if __name__ == '__main__':

    walls = {(1000, 0): (-1000, 0)}
    plain = Plain(walls=walls)
    walker = Walker(1)
    for _ in range(1000):
        plain.move_walker(walker)
        print(walker.get_location())
