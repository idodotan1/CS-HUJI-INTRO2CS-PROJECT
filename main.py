import random
import math
import matplotlib.pyplot as plt
from plain import *
from walker import *
from matplotlib.animation import FuncAnimation
from simulation import *
import argparse
import re
import subprocess
import sys



def valid_obstacle(s: str) -> Tuple[float, float]:
    "The function to validate the obstacles input"
    try:
        # Matches strings like "(1.5,-2)" and converts to tuple (1.5, -2)
        match = re.match(r'\(\s*(-?\d+(\.\d+)?)\s*,\s*(-?\d+(\.\d+)?)\s*\)$', s)
        if match:
            return (float(match.group(1)), float(match.group(3)))
        raise ValueError
    except:
        raise argparse.ArgumentTypeError("Invalid obstacle format. Use '(x,y)'.")


def valid_magic_portal_or_wall(s: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    "The function to validate the magic portals and walls input"
    try:
        # Matches strings like "((1,2),(3,4))" and converts to tuple ((1, 2), (3, 4))
        match = re.match(r'\(\(\s*(-?\d+(\.\d+)?)\s*,\s*(-?\d+(\.\d+)?)\s*\),\s*\(\s*(-?\d+(\.\d+)?)\s*,\s*(-?\d+(\.\d+)?)\s*\)\s*\)$', s)
        if match:
            return ((float(match.group(1)), float(match.group(3))), (float(match.group(5)), float(match.group(7))))
        raise ValueError
    except:
        raise argparse.ArgumentTypeError("Invalid wall or magic portal format. Use '((x1,y1),(x2,y2))'.")


def valid_movement_type(value: str) -> int:
    "The function to validate the movement type input"
    try:
        ivalue = int(value)
        if ivalue < 1 or ivalue > 4:
            raise argparse.ArgumentTypeError(f"{value} is an invalid movement type. Choose a value between 1 and 4.")
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{value} is not a valid integer. Movement type must be an integer between 1 and 4.")


def valid_num_steps(value: str) -> int:
    "The function to validate the number of steps input"
    try:
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(f"{value} is an invalid number of steps. Must be a positive integer.")
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid integer. Number of steps must be a positive integer.")


def valid_num_simulations(value: str) -> int:
    "The function to validate the number of simulations input"
    try:
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid number of simulations. Must be a positive integer.")
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{value} is not a valid integer. Number of simulations must be a positive integer.")


# Parse command line arguments
parser = argparse.ArgumentParser(description='Welcome to the Random Walker Simulation! Its best to run the program through the GUI.'
                                             ' In order to use the GUI run python gui.py or python main.py --gui.')
parser.add_argument('--movement', type=valid_movement_type, help='The movement type for the walker (1-4) 1 for'
                                                                 ' one step at random angle, 2 for random step size(between 0.5 and 1.5) at random angle'
                                                                 ' 3 for one step at 1 of 4 general directions and 4 for one step of 4 at general direction'
                                                                 ' or to start point direction with different probabilities, set default to 1',
                    default=1)
parser.add_argument('--obstacles', type=valid_obstacle, nargs='*', help='List of obstacles as "(x,y)"', default=[])
parser.add_argument('--walls', type=valid_magic_portal_or_wall, nargs='*', help='List of walls as "((x1,y1),(x2,y2))"'
                                                                                ' where first tuple is the starting point of the wall and second tuple is the ending point of the wall',
                    default=[])
parser.add_argument('--magic_portals', type=valid_magic_portal_or_wall, nargs='*', help='List of magic portals,'
                                                                                        ' first tuple is the portal and the second is the destination as "((x1,y1),(x2,y2))" ',
                    default=[])
parser.add_argument('--num_steps', type=valid_num_steps, help='Number of steps per simulation(a natural number), set default to 100',
                    default=100)
parser.add_argument('--num_simulations', type=valid_num_simulations,
                    help='Number of simulations to run(a natural number), set default to 10', default=10)
parser.add_argument('--reset', type=float,
                    help='The probability between 0-1 of the walker to reset to the start point after each step,'
                         ' default is 0', default=0)
parser.add_argument('--gui', action='store_true', help='Run the program through the GUI.')

args = parser.parse_args()

if args.gui:
    print("Running GUI...")
    python_executable = 'C:\\Users\\idodo\\Desktop\\לימודים\\אינטרו\\RandomWalker\\.venv\\Scripts\\python.exe'
    subprocess.run([python_executable, 'gui.py'])
    sys.exit()  # Exit after running the GUI

if args.movement == 4:
    print("You chose movement type 4, please enter the weights for each direction")
    weights = []
    i = 1
    total_1 = False
    while not total_1:
        i = 1
        while len(weights) < 5:
            try:
                weight = float(input(f"Enter the weight for direction {i}: "))
                if weight < 0 or weight > 1:
                    raise argparse.ArgumentTypeError(
                        f"{weight} is an invalid weight. Must be a positive float between 0 and 1.")
                else:
                    weights.append(weight)
                    i += 1
            except ValueError:
                raise argparse.ArgumentTypeError("Not a valid float. Weight must be a float between 0 and 1.")
        if sum(weights) == 1:
            total_1 = True
        else:
            print("The sum of the weights must be 1, please enter the weights again")
            weights = []
    args.weights = weights
# Create a plain with obstacles and magic portals
plain = Plain(obstacles=args.obstacles, magic_portals=dict(args.magic_portals), walls=dict(args.walls))
walker = Walker(movement_type=args.movement, reset=args.reset,
                weights_list=args.weights if args.movement == 4 else None)
simulation = Simulation(plain, walker, args.num_steps, args.num_simulations)
simulation.run_simulations()
print("Done! all simulations are finished.")
graph_of_distances = input(
    "Do you want to see the graph of the distances? enter yes if you want to see it and anything else otherwise:")
if graph_of_distances == "yes":
    simulation.plot_average_distance_from_start()
avg_time_out_of_radius = input(
    "Do you want to see the average time the walker was out of the radius? enter yes if you want to see it and anything else otherwise:")
if avg_time_out_of_radius == "yes":
    print(simulation.get_average_steps_to_exit_radius())
graph_of_distance_from_axis = input(
    "Do you want to see the graph of the distance from the axisis? enter yes if you want to see it and anything else otherwise:")
if graph_of_distance_from_axis == "yes":
    simulation.plot_average_distance_from_axis()
graph_of_cross_axis = input(
    "Do you want to see the graph of the number of times the walker crossed the axis? enter yes if you want to see it and anything else otherwise:")
if graph_of_cross_axis == "yes":
    simulation.plot_axis_crossings()
graph_of_last_simulation = input(
    "Do you want to see the graph of the last simulation? enter yes if you want to see it and anything else otherwise:")
if graph_of_last_simulation == "yes":
    simulation.plot_last_sim_location()

