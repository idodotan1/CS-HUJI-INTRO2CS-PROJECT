import random
import math
import matplotlib.pyplot as plt
from plain import *
from walker import *
from matplotlib.animation import FuncAnimation


class Simulation:
    """
    A class to represent simulations of a walker on a plain. The simulation can be used to run multiple simulations,
    and to calculate and plot the average distance of the walker from the starting point, the average number of steps,
    the average distance from the x and y axes, and the average times the walker crossed the x and y axes over the
    number of steps.
    """
    __EXIT_RADIUS: int = 10

    def __init__(self, plain: Plain, walker: Walker, num_steps: int, num_simulations: int) -> None:
        if not isinstance(num_steps, int) or not isinstance(num_simulations,
                                                            int) or num_steps < 1 or num_simulations < 1:
            raise ValueError("num_steps and num_simulations must be integers and greater than 0")

        self.__walker: Walker = walker
        self.__num_steps: int = num_steps
        self.__num_simulations: int = num_simulations
        self.__plain: Plain = plain
        self.__avg_distances_from_start: List[float] = [0.0] * (num_steps + 1)
        self.__total_steps_to_exit: int = 0
        self.__exit_count: int = 0
        self.__avg_distances_from_axis: Dict[str, List[float]] = {'x': [0.0] * (num_steps + 1),
                                                                  'y': [0.0] * (num_steps + 1)}
        self.__total_axis_crossings: Dict[str, int] = {'x': 0, 'y': 0}
        self.__avg_steps_to_exit: float = 0.0  # Initialized here for clarity, will be computed in __finalize_averages
        self.__avg_axis_crossings: Dict[str, float] = {'x': 0.0, 'y': 0.0}  # Initialized here for clarity

    def __cross_axis(self, last_location: Tuple[float, float]) -> Tuple[bool, bool]:
        "The function checks if the walker crossed the x or y axis and returns the axis crossed or None if no axis was crossed."
        last_x, last_y = last_location
        current_x, current_y = self.__walker.get_x(), self.__walker.get_y()
        y_axis = False
        x_axis = False
        # Check for crossing the y-axis (change in x-coordinate sign)
        if (last_x <= 0 < current_x) or (last_x >= 0 > current_x):
            y_axis = True
        # Check for crossing the x-axis (change in y-coordinate sign)
        if (last_y <= 0 < current_y) or (last_y >= 0 > current_y):
            x_axis = True
        # No axis crossing
        return y_axis, x_axis

    def __run_simulation(self) -> Tuple[List[float], int, Dict[str, List[float]], Dict[str, int]]:
        """The method that runs a single simulation of the walker on the plain and returns
         all the statistics of the simulation"""
        distances = [0.0]
        steps_to_exit = 0
        distances_from_axis = {'x': [0.0], 'y': [0.0]}
        axis_crossings = {'x': 0, 'y': 0}
        self.__walker.set_x(0)
        self.__walker.set_y(0)
        self.__walker.clear_history()
        for i in range(1, self.__num_steps + 1):
            last_location = self.__walker.get_location()
            self.__plain.move_walker(self.__walker)
            # Check for axis crossings in a single call
            y_axis_crossed, x_axis_crossed = self.__cross_axis(last_location)
            # Increment the counters based on the results
            if x_axis_crossed:
                axis_crossings['x'] += 1
            if y_axis_crossed:
                axis_crossings['y'] += 1
            # Calculate distances from axis
            distances_from_axis['y'].append(abs(self.__walker.get_x()))
            distances_from_axis['x'].append(abs(self.__walker.get_y()))
            # Calculate overall distance from the starting point
            distance = math.sqrt(self.__walker.get_x() ** 2 + self.__walker.get_y() ** 2)
            distances.append(distance)
            if distance > self.__EXIT_RADIUS and steps_to_exit == 0:
                steps_to_exit = i
        return distances, steps_to_exit, distances_from_axis, axis_crossings

    def __update_averages(self, distances: List[float], steps_to_exit: int, distances_from_axis: Dict[str, List[float]],
                          axis_crossings: Dict[str, int]) -> None:
        """The function updates the average distances from the starting point, the average number of steps to exit the radius,
         the average distances from the x and y axes, and the average times the walker crossed the x and y axes."""

        for i in range(self.__num_steps + 1):
            self.__avg_distances_from_start[i] += distances[i]
            self.__avg_distances_from_axis['x'][i] += distances_from_axis['x'][i]
            self.__avg_distances_from_axis['y'][i] += distances_from_axis['y'][i]

        if steps_to_exit > 0:
            self.__total_steps_to_exit += steps_to_exit
            self.__exit_count += 1

        self.__total_axis_crossings['x'] += axis_crossings['x'] - 1
        if self.__total_axis_crossings['x'] < 0:
            self.__total_axis_crossings['x'] = 0
        self.__total_axis_crossings['y'] += axis_crossings['y'] - 1
        if self.__total_axis_crossings['y'] < 0:
            self.__total_axis_crossings['y'] = 0

    def __finalize_averages(self) -> None:
        """The function finalizes the average distances from the starting point, the average number of steps to exit the radius,
         the average distances from the x and y axes, and the average times the walker crossed the x and y axes."""

        divisor = self.__num_simulations
        for i in range(self.__num_steps + 1):
            self.__avg_distances_from_start[i] /= divisor
            self.__avg_distances_from_axis['x'][i] /= divisor
            self.__avg_distances_from_axis['y'][i] /= divisor

        self.__avg_steps_to_exit = (self.__total_steps_to_exit / self.__exit_count) if self.__exit_count > 0 else None
        self.__avg_axis_crossings = {axis: self.__total_axis_crossings[axis] / divisor for axis in ['x', 'y']}

    def run_simulations(self) -> None:
        """The function runs the specified number of simulations and calculates the average distances from the starting point,
         the average number of steps to exit the radius, the average distances from the x and y axes, and the average times the walker crossed the x and y axis."""
        for _ in range(self.__num_simulations):
            distances, steps_to_exit, distances_from_axis, axis_crossings = self.__run_simulation()
            self.__update_averages(distances, steps_to_exit, distances_from_axis, axis_crossings)
        self.__finalize_averages()

    def get_average_distance_after_steps(self, steps: int) -> float:
        return self.__avg_distances_from_start[steps]

    def get_average_steps_to_exit_radius(self) -> float:
        return self.__avg_steps_to_exit

    def get_average_distance_from_axis_after_steps(self, steps: int, axis: str) -> float:

        return self.__avg_distances_from_axis[axis][steps]

    def get_average_times_crossed_axis(self, axis: str) -> float:

        return self.__avg_axis_crossings[axis]

    def plot_average_distance_from_start(self) -> None:
        """
        Plot the average distance of the walker from the starting point over the number of steps.
        """
        plt.plot(range(self.__num_steps + 1), self.__avg_distances_from_start)
        plt.xlabel('Number of Steps')
        plt.ylabel('Average Distance from Starting Point')
        plt.title('Average Distance from Starting Point Over Steps')
        plt.grid(True)
        plt.show()

    def plot_average_distance_from_axis(self) -> None:
        """
        Plot the average distance of the walker from the x and y axes over the number of steps.
        """
        plt.plot(range(self.__num_steps + 1), self.__avg_distances_from_axis['x'], label='X Axis')
        plt.plot(range(self.__num_steps + 1), self.__avg_distances_from_axis['y'], label='Y Axis')
        plt.xlabel('Number of Steps')
        plt.ylabel('Average Distance from Axis')
        plt.title('Average Distance from Axis Over Steps')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_axis_crossings(self) -> None:
        """
        Plot the average times the walker crossed the x and y axes.
        """
        plt.bar(['X Axis', 'Y Axis'], [self.__avg_axis_crossings['x'], self.__avg_axis_crossings['y']])
        plt.xlabel('Axis')
        plt.ylabel('Average Crossings')
        plt.title('Average Crossings of Axis')
        plt.grid(True)
        plt.show()

    def plot_last_sim_location(self):
        "The method that plots the last simulation of the walker."

        x_coords = [pos[0] for pos in self.__walker.get_history()]
        y_coords = [pos[1] for pos in self.__walker.get_history()]
        plt.plot(x_coords, y_coords, marker='o', linestyle='-')
        plt.title("Random Walker Movement")
        plt.xlabel("X-coordinate")
        plt.ylabel("Y-coordinate")
        plt.grid(True)
        plt.show()


if __name__ == '__main__':
    walker1 = Walker(2)
    plain1 = Plain([], {}, {(1000, 0): (-1000, 0)})
    new_sim = Simulation(plain1, walker1, 100, 1)
    new_sim.run_simulations()
    new_sim.plot_axis_crossings()
    new_sim.plot_average_distance_from_axis()
    new_sim.plot_average_distance_from_start()
    new_sim.plot_last_sim_location()
