import tkinter as tk
from simulation import *
from plain import *
from walker import *
from tkinter import messagebox, LabelFrame, Label, Entry, Button, Radiobutton, StringVar, IntVar, Toplevel, BooleanVar


class Already_Exist(Exception):
    """A subclass exception that is raised if the obstacle or portal or wall already exists"""

    def __init__(self, message="The item already exists"):
        self.message = message
        super().__init__(message)


class ResultsDialog:
    "The class used to represent the results dialog for the simulation results"

    def __init__(self, master, simulation):
        self.top = Toplevel(master)
        self.top.title("Simulation Results")
        self.simulation = simulation

        Button(self.top, text="Average Distance from Start", command=self.show_avg_distance_from_start, width=25).pack(
            pady=5, padx=5)
        Button(self.top, text="Average Distance from Axis", command=self.show_avg_distance_from_axis, width=25).pack(
            pady=5, padx=5)
        Button(self.top, text="Average Steps to Exit Radius", command=self.show_avg_steps_to_exit_radius,
               width=25).pack(pady=5, padx=5)
        Button(self.top, text="Axes crossing stats", command=self.show_axes_crossing_stats, width=25).pack(pady=5,
                                                                                                           padx=5)
        Button(self.top, text="Show last simulation graph", command=self.show_last_simulation_graph, width=25).pack(
            pady=5, padx=5)

    def show_avg_distance_from_start(self):
        self.simulation.plot_average_distance_from_start()

    def show_avg_distance_from_axis(self):
        self.simulation.plot_average_distance_from_axis()

    def show_axes_crossing_stats(self):
        self.simulation.plot_axis_crossings()

    def show_avg_steps_to_exit_radius(self):
        avg_steps = self.simulation.get_average_steps_to_exit_radius()
        if avg_steps is None:
            tk.messagebox.showinfo("Average Steps to Exit Radius", "The walker never exited the radius.")
        else:
            tk.messagebox.showinfo("Average Steps to Exit Radius", f"Average steps to exit radius: {avg_steps}")

    def show_last_simulation_graph(self):
        self.simulation.plot_last_sim_location()


class RandomWalkerGUI:
    "The class used to represent the main Random Walker GUI"

    def __init__(self, master: tk.Tk):
        self.__master = master
        master.title("Random Walker Simulation")

        # Movement type with callback to show weight entries if needed
        self.__movement_type = IntVar(value=1)  # Default movement type
        self.__create_movement_buttons()

        # Weights for movement type 4
        self.__weights = [StringVar(value='0.2') for _ in range(5)]  # Default weights
        self.__weights_entries = []

        # Number of steps and simulations
        self.__num_steps = StringVar(value='100')  # Default number of steps
        self.__num_simulations = StringVar(value='10')  # Default number of simulations
        self.__create_step_simulation_entries()

        # Obstacles and Magic Portals inputs
        self.__obstacles = []
        self.__magic_portals = {}
        self.__walls = {}
        self.__create_obstacle_portal_walls_entries()

        # Obstacles and Portals display
        self.__obstacles_frame = LabelFrame(master, text="Obstacles")
        self.__obstacles_frame.grid(row=7, column=0, columnspan=5, sticky='ew')
        self.__portals_frame = LabelFrame(master, text="Magic Portals")
        self.__portals_frame.grid(row=8, column=0, columnspan=5, sticky='ew')
        self.__walls_frame = LabelFrame(master, text="Walls")
        self.__walls_frame.grid(row=9, column=0, columnspan=5, sticky='ew')

        # Reset button display
        self.__reset = BooleanVar(value=False)
        self.__reset_value = StringVar(value='0.0')
        self.__create_reset_frame()

        # Submit button
        self.__submit_button = Button(master, text="Run Simulation", command=self.__run_simulation)
        self.__submit_button.grid(row=10, columnspan=5, sticky='ew')

        # Update GUI based on movement type
        self.__update_movement_type()

    def __create_reset_frame(self):
        "The method used to create the reset frame for the reset option"
        reset_frame = LabelFrame(self.__master, text="Reset option")
        explanation = Label(reset_frame,
                            text="If you want the walker to have a chance to reset to the start point after each step,"
                                 " enter the probability of reseting back to start between 0 and 1.",
                            font=('Helvetica', 10), relief='groove', padx=10, pady=10, width=180)
        explanation.pack()
        reset_frame.grid(row=3, column=0, columnspan=5, sticky='ew')
        self.__reset_value_entry = Entry(reset_frame, textvariable=self.__reset_value, width=5, state='disabled')
        button2 = Radiobutton(reset_frame, text="Yes", command=self.__update_reset, value=True, variable=self.__reset)
        button1 = Radiobutton(reset_frame, text="No", command=self.__update_reset, value=False, variable=self.__reset)
        button1.pack(side='left')
        button2.pack(side='left')
        self.__reset_value_entry.pack(side='left')

    def __update_reset(self):
        "The method used to update the reset value entry based on the reset value"
        if self.__reset.get():
            self.__reset_value_entry.config(state='normal')
        else:
            self.__reset_value_entry.config(state='disabled')

    def __create_weights_frame(self):
        "The method used to create the weights frame for movement type 4"
        self.weights_frame = LabelFrame(self.__master, text="Direction Weights")

        for i, weight_var in enumerate(self.__weights):
            Label(self.weights_frame, text=f"Weight {i + 1}:").pack(side='left')
            entry = Entry(self.weights_frame, textvariable=weight_var, width=5)
            entry.pack(side='left', padx=2)
            self.__weights_entries.append(entry)

    def __create_movement_buttons(self):
        "The method used to create the movement type buttons"

        movement_frame = LabelFrame(self.__master, text="Movement Type")
        explanation = Label(movement_frame,
                            text="1 for random angle and constant step size, 2 for random step size, 3 for"
                                 " 1 of 4 directions, 4 for 1 of 4 directions and back to start with different probabilities",
                            font=('Helvetica', 10), relief='groove', padx=10, pady=10, width=180)
        explanation.pack()
        movement_frame.grid(row=0, column=0, columnspan=5, sticky='ew')
        for i in range(1, 5):
            button = Radiobutton(movement_frame, text=f"Type {i}", variable=self.__movement_type, value=i,
                                 command=self.__update_movement_type)
            button.pack(side='left')

    def __update_movement_type(self):
        "The method used to update the movement type"

        # Clear previous weight entries if any and disable them
        for entry in self.__weights_entries:
            entry.config(state='disabled')
        self.__weights_entries.clear()

        weights_frame = LabelFrame(self.__master, text="Direction Weights")
        explanation = Label(weights_frame,
                            text="If you choose movement 4, enter the weights for each direction(1 is up, 2 is down, 3 is right, 4 is left, 5 is to origin)."
                                 "The sum of the weights must be equal to 1.", font=('Helvetica', 10), relief='groove',
                            padx=10, pady=10, width=180)
        explanation.pack()
        weights_frame.grid(row=1, column=0, columnspan=6, sticky='ew')
        for i, weight_var in enumerate(self.__weights):
            Label(weights_frame, text=f"Weight {i + 1}:").pack(side='left')
            entry = Entry(weights_frame, textvariable=weight_var, width=5,
                          state='normal' if self.__movement_type.get() == 4 else 'disabled')
            # The defualt value of the weights is 0.2 and the state is disabled unless the movement type is 4
            entry.pack(side='left', padx=2)
            self.__weights_entries.append(entry)

    def __create_step_simulation_entries(self):
        "The method used to define the number of steps and simulations entries"

        steps_frame = LabelFrame(self.__master, text="Simulation Settings")
        steps_frame.grid(row=2, column=0, columnspan=5, sticky='ew')
        Label(steps_frame, text="Number of Steps:").pack(side='left')
        Entry(steps_frame, textvariable=self.__num_steps).pack(side='left')
        Label(steps_frame, text="Number of Simulations:").pack(side='left')
        Entry(steps_frame, textvariable=self.__num_simulations).pack(side='left')

    def __create_obstacle_portal_walls_entries(self):
        "The method used to define the obstacles, magic portals and walls entries"

        obstacle_frame = LabelFrame(self.__master, text="Add Obstacle")
        explanation = Label(obstacle_frame,
                            text="If you want to add a single point obstacle, enter the x and y coordinates and click Add."
                                 " The obstacles you entered will be displayed in the list below.",
                            font=('Helvetica', 10), relief='groove', padx=10, pady=10, width=180)
        explanation.pack()
        obstacle_frame.grid(row=4, column=0, columnspan=5, sticky='ew')
        self.__obstacle_x = StringVar()
        self.__obstacle_y = StringVar()
        Label(obstacle_frame, text="X:").pack(side='left')
        Entry(obstacle_frame, textvariable=self.__obstacle_x, width=5).pack(side='left')
        Label(obstacle_frame, text="Y:").pack(side='left')
        Entry(obstacle_frame, textvariable=self.__obstacle_y, width=5).pack(side='left')
        Button(obstacle_frame, text="Add", command=self.__add_obstacle).pack(side='left')

        portal_frame = LabelFrame(self.__master, text="Add Magic Portal")
        explanation = Label(portal_frame,
                            text="If you want to add a magic portal, enter the x and y coordinates of the entry to the portal"
                                 "and the x and y coordinates of the destination of the portal and click Add.",
                            font=('Helvetica', 10), relief='groove', padx=10, pady=10, width=180)
        explanation.pack()
        portal_frame.grid(row=5, column=0, columnspan=5, sticky='ew')
        self.__portal_x1 = StringVar()
        self.__portal_y1 = StringVar()
        self.__portal_x2 = StringVar()
        self.__portal_y2 = StringVar()
        Label(portal_frame, text="Portal X1:").pack(side='left')
        Entry(portal_frame, textvariable=self.__portal_x1, width=5).pack(side='left')
        Label(portal_frame, text="Y1:").pack(side='left')
        Entry(portal_frame, textvariable=self.__portal_y1, width=5).pack(side='left')
        Label(portal_frame, text="X2:").pack(side='left')
        Entry(portal_frame, textvariable=self.__portal_x2, width=5).pack(side='left')
        Label(portal_frame, text="Y2:").pack(side='left')
        Entry(portal_frame, textvariable=self.__portal_y2, width=5).pack(side='left')
        Button(portal_frame, text="Add", command=self.__add_magic_portal).pack(side='left')

        wall_frame = LabelFrame(self.__master, text="Add Wall")
        wall_frame.grid(row=6, column=0, columnspan=5, sticky='ew')
        explanation = Label(wall_frame,
                            text="If you want to add a wall, enter the x and y coordinates of the starting point of the wall"
                                 "and the x and y coordinates of the ending point of the wall and click Add.",
                            font=('Helvetica', 10), padx=10, pady=10, width=180, relief='groove')
        explanation.pack()
        self.__wall_x1 = StringVar()
        self.__wall_y1 = StringVar()
        self.__wall_x2 = StringVar()
        self.__wall_y2 = StringVar()
        Label(wall_frame, text="Wall start X:").pack(side='left')
        Entry(wall_frame, textvariable=self.__wall_x1, width=5).pack(side='left')
        Label(wall_frame, text="Start Y:").pack(side='left')
        Entry(wall_frame, textvariable=self.__wall_y1, width=5).pack(side='left')
        Label(wall_frame, text="End X:").pack(side='left')
        Entry(wall_frame, textvariable=self.__wall_x2, width=5).pack(side='left')
        Label(wall_frame, text="End Y:").pack(side='left')
        Entry(wall_frame, textvariable=self.__wall_y2, width=5).pack(side='left')
        Button(wall_frame, text="Add", command=self.__add_wall).pack(side='left')

    def __valid_obstacle(self, obstacle: Tuple[float, float]) -> bool:
        "The method used to check if the obstacle is valid"
        if obstacle in self.__magic_portals or obstacle in self.__magic_portals.values():
            return False
        for wall in self.__walls:
            if self.__calculate_det(wall, self.__walls[wall], obstacle) == 0:
                # If the determinant is 0 then the obstacle is on the wall
                return False
        return True

    def __add_obstacle(self):
        "The method used to add an obstacle to the obstacles list"
        try:
            x = float(self.__obstacle_x.get())
            y = float(self.__obstacle_y.get())
            new_obstacle = (x, y)
            if new_obstacle in self.__obstacles:
                raise Already_Exist
            if not self.__valid_obstacle(new_obstacle):
                raise ValueError
            self.__obstacles.append((x, y))
            self.__update_lists_display()
            # Now we reset the entry fields
            self.__obstacle_x.set('')
            self.__obstacle_y.set('')
        except ValueError:
            messagebox.showerror("Error", "Invalid obstacle coordinates")
        except Already_Exist:
            messagebox.showerror("Error", "The obstacle already exists")

    def __calculate_det(self, point1: Tuple[float, float], point2: Tuple[float, float],
                        point3: Tuple[float, float]) -> float:
        """The method used to calculate the determinant of the 3 points
               in order to determine if a point is in the line created by the other two points"""

        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = point3
        return (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)

    def __valid_magic_portal(self, new_portal: Tuple[Tuple[float, float], Tuple[float, float]]) -> bool:
        "The method used to check if the magic portal is valid"

        if new_portal[0] == new_portal[1]:
            return False
        if new_portal[0] in self.__obstacles or new_portal[1] in self.__obstacles:
            return False
        for wall in self.__walls:
            if (self.__calculate_det(wall, self.__walls[wall], new_portal[0]) == 0 or
                    self.__calculate_det(wall, self.__walls[wall], new_portal[1]) == 0):
                return False
        return True

    def __add_magic_portal(self):
        try:
            x1 = float(self.__portal_x1.get())
            y1 = float(self.__portal_y1.get())
            x2 = float(self.__portal_x2.get())
            y2 = float(self.__portal_y2.get())
            new_portal = ((x1, y1), (x2, y2))
            if not self.__valid_magic_portal(new_portal):
                raise ValueError
            if new_portal[0] in self.__magic_portals or new_portal[1] in self.__magic_portals:
                raise Already_Exist
            self.__magic_portals[new_portal[0]] = new_portal[1]
            self.__update_lists_display()
            self.__portal_x1.set('')
            self.__portal_y1.set('')
            self.__portal_x2.set('')
            self.__portal_y2.set('')
        except ValueError:
            messagebox.showerror("Error", "Invalid magic portal coordinates")
        except Already_Exist:
            messagebox.showerror("Error", "The portal already exists")

    def __valid_wall(self, new_wall: Tuple[Tuple[float, float], Tuple[float, float]]) -> bool:
        "The method used to check if the wall is valid"

        if new_wall[0] in self.__obstacles or new_wall[1] in self.__obstacles:
            return False
        if (new_wall[0] in self.__magic_portals or new_wall[1] in self.__magic_portals or
                new_wall[0] in self.__magic_portals.values() or new_wall[1] in self.__magic_portals.values()):
            return False
        for obstacles in self.__obstacles:
            if self.__calculate_det(new_wall[0], new_wall[1], obstacles) == 0:
                return False
        for portal in self.__magic_portals:
            if (self.__calculate_det(new_wall[0], new_wall[1], portal) == 0 or
                    self.__calculate_det(new_wall[0], new_wall[1], self.__magic_portals[portal]) == 0):
                return False
        return True

    def __add_wall(self):
        "The method used to add a wall to the walls list"

        try:
            x1 = float(self.__wall_x1.get())
            y1 = float(self.__wall_y1.get())
            x2 = float(self.__wall_x2.get())
            y2 = float(self.__wall_y2.get())
            new_wall = ((x1, y1), (x2, y2))
            if not self.__valid_wall(new_wall):
                raise ValueError
            if new_wall[0] in self.__walls or new_wall[1] in self.__walls:
                raise Already_Exist
            self.__walls[new_wall[0]] = new_wall[1]
            self.__update_lists_display()
            self.__wall_x1.set('')
            self.__wall_y1.set('')
            self.__wall_x2.set('')
            self.__wall_y2.set('')
        except ValueError:
            messagebox.showerror("Error", "Invalid wall coordinates")
        except Already_Exist:
            messagebox.showerror("Error", "The wall already exists")

    def __update_lists_display(self):
        # Clear the current display frames
        for widget in self.__obstacles_frame.winfo_children():
            widget.destroy()
        for widget in self.__portals_frame.winfo_children():
            widget.destroy()
        for widget in self.__walls_frame.winfo_children():
            widget.destroy()

        # Update the obstacles frame with the current obstacles list
        for obstacle in self.__obstacles:
            Label(self.__obstacles_frame, text=str(obstacle)).pack()

        # Update the portals frame with the current magic portals list
        for portal in self.__magic_portals:
            Label(self.__portals_frame, text=(str(portal) + "," + str(self.__magic_portals[portal]))).pack()

        for wall in self.__walls:
            Label(self.__walls_frame, text=(str(wall) + "," + str(self.__walls[wall]))).pack()

    def __run_simulation(self):
        try:
            try:
                num_steps = int(self.__num_steps.get())
                num_simulations = int(self.__num_simulations.get())
            except ValueError:
                raise ValueError("Number of steps and simulations must be positive integers.")
            if num_steps <= 0 or num_simulations <= 0:
                raise ValueError("Number of steps and simulations must be positive integers.")
            if self.__reset.get():
                try:
                    self.__reset_value = float(self.__reset_value_entry.get())
                    epsilon = 1e-10
                    if not (0 + epsilon < self.__reset_value < 1 - epsilon):
                        raise ValueError("Invalid reset value. Reset value must be a float between 0 and 1.")
                except ValueError:
                    raise ValueError("Invalid reset value. Reset value must be a float between 0 and 1.")
            else:
                self.__reset_value = 0
            if self.__movement_type.get() == 4:
                try:
                    weights = [float(weight.get()) for weight in self.__weights]
                except ValueError:
                    raise ValueError("Invalid weight format. Weights must be positive floats.")
                if sum(weights) != 1:
                    raise ValueError("The sum of the weights must be equal to 1.")

                walker = Walker(movement_type=4, weights_list=weights, reset=self.__reset_value)
            else:
                walker = Walker(movement_type=self.__movement_type.get(), reset=self.__reset_value)
            plain = Plain(self.__obstacles, dict(self.__magic_portals), dict(self.__walls))
            simulation = Simulation(plain, walker, num_steps, num_simulations)
            simulation.run_simulations()
            ResultsDialog(self.__master, simulation)
        except ValueError as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    gui = RandomWalkerGUI(root)
    root.mainloop()
