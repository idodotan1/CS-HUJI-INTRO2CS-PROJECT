import random
import math
import matplotlib.pyplot as plt
from plain import *
from walker import *
from matplotlib.animation import FuncAnimation

class Simulation:
    """
    A class representing a simulation of walker movement on a plain.

    Attributes:
        walker (Walker): The walker object.
        num_steps (int): The number of steps for each simulation run.
        num_simulations (int): The number of simulations to run.
        plain (Plain): The plain where the walker moves.
        avg_distances (list): A list to store the average distances of the walker from the starting point.
        avg_steps_to_exit (list): A list to store the average steps required for the walker to exit a radius of 10 from (0, 0).
        avg_distances_from_axis (dict): A dictionary to store the average distances of the walker from the specified axis.
        axis_crossings (dict): A dictionary to store the average times the walker crossed each axis.
    """

    def __init__(self, plain, walker, num_steps, num_simulations):
        """
        Initialize the simulation with the provided parameters.

        Parameters:
            walker (Walker): The walker object.
            num_steps (int): The number of steps for each simulation run.
            num_simulations (int): The number of simulations to run.
        """
        self.walker = walker
        self.num_steps = num_steps
        self.num_simulations = num_simulations
        self.plain = plain
        self.avg_distances_from_start = []
        self.avg_steps_to_exit = 0
        self.avg_distances_from_axis = {'x': [], 'y': []}
        self.avg_axis_crossings = {'x': 0, 'y': 0}

    def run_simulation(self):
        """
        Run the simulation 1 time and returns all the data from the simulation
        """
        distances = [0.0]
        steps_to_exit = 0
        distances_from_axis = {'x': [0.0], 'y': [0.0]}
        axis_crossings = {'x': 0, 'y': 0}
        self.walker.set_x(0)
        self.walker.set_y(0)
        currently_on_x = True
        currently_on_y = True
        for i in range(1,self.num_steps+1):
            self.plain.move_walker(self.walker)
            # Count axis crossings
            if self.walker.get_x() == 0 and not currently_on_y:
                axis_crossings['y'] += 1
                currently_on_y = True
            elif self.walker.get_x() != 0:
                currently_on_y = False
            if self.walker.get_y() == 0 and not currently_on_x:
                axis_crossings['x'] += 1
                currently_on_x = True
            elif self.walker.get_y() != 0:
                currently_on_x = False
            # Calculate distance from axis
            distances_from_axis['x'].append(abs(self.walker.get_x()))
            distances_from_axis['y'].append(abs(self.walker.get_y()))

            # Calculate distance from starting point
            distance = ((self.walker.get_x()) ** 2 + (self.walker.get_y()) ** 2) ** 0.5
            distances.append(distance)
            # Check if walker exits radius of 10 from (0, 0)
            if distance > 10:
                steps_to_exit = i
        return distances,steps_to_exit,distances_from_axis,axis_crossings

    def update_avg_distance_from_start(self,distance_list):
        """
        This function gets the list of average distances of the walker from
        the start point at a simulation and updates the simulation avg_distance_from_start
        :param distance_list: a list of distances
        :return: None
        """
        for i in range(self.num_steps):
            self.avg_distances_from_start[i] = (self.avg_distances_from_start[i] + distance_list[i])/2

    def update_avg_stpes_to_exit(self,steps_to_exit):
        """
        This function updates the avg_steps_to_exit attribute
        :param steps_to_exit: the number of steps it took to exit in a simulation
        :return: None
        """
        if steps_to_exit != 0:
            self.avg_steps_to_exit = (self.avg_steps_to_exit + steps_to_exit)/2

    def update_avg_distance_from_axis(self,avg_dist_dict):
        """
         This function updates the avg_distance_from_axis attribute
        :param avg_dist_dict: a dict that holds the avg distance from x and y axis at
        each step
        :return: None
        """
        for i in range(self.num_steps):
            self.avg_distances_from_axis["x"][i] = ( self.avg_distances_from_axis["x"][i]+avg_dist_dict["x"][i])/2
            self.avg_distances_from_axis["y"][i] = (self.avg_distances_from_axis["y"][i] + avg_dist_dict["y"][i]) / 2

    def update_avg_axis_crossing(self,axis_crossing_dict):
        """
         This function updates the avg_axis_crossing attribute
        :param axis_crossing_dict: a dict with number of crossing of each axis in a simulation
        :return: None
        """
        self.avg_axis_crossings["x"] = ( self.avg_axis_crossings["x"]+axis_crossing_dict["x"])/2
        self.avg_axis_crossings["y"] = ( self.avg_axis_crossings["y"]+axis_crossing_dict["y"])/2

    def run_simulations(self):
        for i in range(self.num_simulations):
            distances,steps_to_exit,distances_from_axis,axis_crossings = self.run_simulation()
            if i == 0:
                self.avg_distances_from_start = distances
                self.avg_steps_to_exit = steps_to_exit
                self.avg_distances_from_axis = distances_from_axis
                self.avg_axis_crossings=axis_crossings
            else:
                self.update_avg_distance_from_start(distances)
                self.update_avg_stpes_to_exit(steps_to_exit)
                self.update_avg_distance_from_axis(distances_from_axis)
    def average_distance_after_steps(self, steps):
        """
        Get the average distance of the walker from the starting point after a specified number of steps.

        Parameters:
            steps (int): The number of steps.

        Returns:
            float: The average distance of the walker from the starting point.
        """
        return self.avg_distances_from_start[steps]

    def average_steps_to_exit_radius(self):
        """
        Get the average number of steps required for the walker to exit a radius of 10 from (0, 0).

        Returns:
            float: The average number of steps required for the walker to exit the radius.
        """
        return self.avg_steps_to_exit

    def average_distance_from_axis_after_steps(self, steps, axis):
        """
        Get the average distance of the walker from a specified axis after a specified number of steps.

        Parameters:
            steps (int): The number of steps.
            axis (str): The axis ('x' or 'y').

        Returns:
            float: The average distance of the walker from the specified axis.
        """
        return self.avg_distances_from_axis[axis][steps]

    def average_times_crossed_axis(self, axis):
        """
        Get the average times the walker crossed a specified axis in all simulations.

        Parameters:
            axis (str): The axis ('x' or 'y').

        Returns:
            float: The average times the walker crossed the specified axis.
        """
        return self.avg_axis_crossings[axis]

    def plot_average_distance_from_start(self):
        """
        Plot the average distance of the walker from the starting point over the number of steps.
        """
        plt.plot(range(self.num_steps + 1), self.avg_distances_from_start)
        plt.xlabel('Number of Steps')
        plt.ylabel('Average Distance from Starting Point')
        plt.title('Average Distance from Starting Point Over Steps')
        plt.grid(True)
        plt.show()

    def plot_average_distance_from_axis(self):
        """
        Plot the average distance of the walker from the x and y axes over the number of steps.
        """
        plt.plot(range(self.num_steps + 1), self.avg_distances_from_axis['x'], label='X Axis')
        plt.plot(range(self.num_steps + 1), self.avg_distances_from_axis['y'], label='Y Axis')
        plt.xlabel('Number of Steps')
        plt.ylabel('Average Distance from Axis')
        plt.title('Average Distance from Axis Over Steps')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_axis_crossings(self):
        """
        Plot the average times the walker crossed the x and y axes.
        """
        plt.bar(['X Axis', 'Y Axis'], [self.avg_axis_crossings['x'], self.avg_axis_crossings['y']])
        plt.xlabel('Axis')
        plt.ylabel('Average Crossings')
        plt.title('Average Crossings of Axis')
        plt.grid(True)
        plt.show()


    def endless_simulation(self):
        """
        Run an endless simulation with animation.
        """
        fig, ax = plt.subplots()
        ax.set_xlim(-40, 40)
        ax.set_ylim(-40, 40)

        # Initialize the walker's position
        self.walker.set_x(0)
        self.walker.set_y(0)
        line, = ax.plot([], [], lw=2)

        def init():
            return line,

        def update(frame):
            self.plain.move_walker(self.walker)
            x_data, y_data = line.get_data()
            x_data = [*x_data, self.walker.get_x()]
            y_data = [*y_data, self.walker.get_y()]
            line.set_data(x_data, y_data)
            return line,

        ani = FuncAnimation(fig, update, frames=range(100), init_func=init, blit=True, interval=50)
        plt.xlabel('X Axis')
        plt.ylabel('Y Axis')
        plt.title('Endless Walker Simulation')
        plt.grid(True)
        plt.show()

# Assuming Simulation object is already instantiated

# Plotting examples


if __name__ == '__main__':
    walker1 = Walker(3)
    plain1 = Plain()
    new_sim = Simulation(plain1,walker1,1000,1)
    new_sim.run_simulations()
    print(new_sim.average_distance_after_steps(50))
    print(new_sim.average_distance_from_axis_after_steps(30,"x"))
    print(new_sim.average_distance_from_axis_after_steps(20,"y"))
    print(new_sim.average_steps_to_exit_radius())
    print(new_sim.average_times_crossed_axis("x"))
    print(new_sim.average_times_crossed_axis("x"))
    print(new_sim.average_times_crossed_axis("y"))
    new_sim.endless_simulation()