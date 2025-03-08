import random
import math
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional


class Walker:
    def __init__(self, movement_type: int = 1, weights_list: Optional[List[float]] = None, reset: float = 0) -> None:
        self.__x: float = 0.0
        self.__y: float = 0.0
        self.__movement_type: int = movement_type
        self.__history: List[Tuple[float, float]] = [(self.__x, self.__y)]
        self.__weights_list: List[float] = weights_list if weights_list is not None and len(weights_list) == 5 else [
            0.2, 0.2, 0.2, 0.2, 0.2]
        self.__reset = reset

    def set_location(self, location: Tuple[float, float]) -> None:
        self.__x, self.__y = location

    def get_x(self) -> float:
        return self.__x

    def set_x(self, x: float) -> None:
        self.__x = x

    def get_y(self) -> float:
        return self.__y

    def set_y(self, y: float) -> None:
        self.__y = y

    def get_movement_type(self) -> int:
        return self.__movement_type

    def set_movement_type(self, movement_type: int) -> None:
        self.__movement_type = movement_type

    def back_to_origin(self) -> Tuple[float, float]:
        "The method to calculate the direction the walker needs to go in order to return back to the origin"
        if self.__x == 0 and self.__y == 0:
            return (0, 0)  # Already at the origin

        theta = math.atan2(-self.__y, -self.__x)
        step_x = math.cos(theta)
        step_y = math.sin(theta)
        return (step_x, step_y)

    def reset(self) -> bool:
        "The method to check if the random reset of the walker is set"
        if self.__reset > 0:
            reset = random.choices([True, False], weights=[self.__reset, 1 - self.__reset])[0]
            return reset
        return False

    def move(self) -> bool:
        "The method to move the walker in the plain, returns True if the walker is reset, False otherwise"
        if self.reset():
            self.__x = 0
            self.__y = 0
            return True
        else:
            dx = 0.0
            dy = 0.0
            if self.__movement_type == 1:
                angle = random.uniform(0, 2 * math.pi)
                dx = math.cos(angle)
                dy = math.sin(angle)
            elif self.__movement_type == 2:
                angle = random.uniform(0, 2 * math.pi)
                step_size = random.uniform(0.5, 1.5)
                dx = step_size * math.cos(angle)
                dy = step_size * math.sin(angle)
            elif self.__movement_type == 3:
                direction = random.choices([(0, 1), (0, -1), (1, 0), (-1, 0)])[0]
                dx, dy = direction
            elif self.__movement_type == 4:
                back_to_origin = self.back_to_origin()
                probabilities = [(0, 1), (0, -1), (1, 0), (-1, 0), back_to_origin]
                weights = self.__weights_list  # Adjust probabilities as needed
                dx, dy = random.choices(population=probabilities, weights=weights)[0]
            self.__x += dx
            self.__y += dy
            return False

    def get_location(self) -> Tuple[float, float]:
        return (self.__x, self.__y)

    def get_history(self) -> List[Tuple[float, float]]:
        return self.__history

    def add_to_history(self, location: Tuple[float, float]) -> None:
        "The method to add a location to the walker's history"
        self.__history.append(location)
    def clear_history(self) -> None:
        "The method to clear the walker's history"
        self.__history = [(self.__x, self.__y)]


if __name__ == '__main__':
    walker = Walker(movement_type=1, reset=0.1)

    # Perform random walk for 10000 steps
    for _ in range(100):
        walker.move()

    # Extract x and y coordinates from the walker's history
    x_coords = [pos[0] for pos in walker.get_history()]
    y_coords = [pos[1] for pos in walker.get_history()]

    # Plot the walker's movement
    plt.plot(x_coords, y_coords, marker='o', linestyle='-')
    plt.title("Random Walker Movement")
    plt.xlabel("X-coordinate")
    plt.ylabel("Y-coordinate")
    plt.grid(True)
    plt.show()
