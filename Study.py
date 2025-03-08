import tkinter as tk
from tkinter import messagebox
class ExampleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Create an IntVar to hold a number
        self.__num_steps = tk.IntVar()

        # Create a frame to hold the Entry widget
        steps_frame = tk.Frame(self)
        steps_frame.pack(pady=20)

        # Create the Entry widget with textvariable linked to __num_steps
        entry = tk.Entry(steps_frame, textvariable=self.__num_steps)
        entry.pack(side='left')

        # Button to display the current value of __num_steps
        button = tk.Button(self, text="Show Value", command=self.show_value)
        button.pack(pady=10)

    def show_value(self):
        # Get the value from __num_steps and show it in a dialog
        value = self.__num_steps.get()
        tk.messagebox.showinfo("Current Value", f"The value is {value}")

# Create and run the application
app = ExampleApp()
app.mainloop()
