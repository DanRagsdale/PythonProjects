# Simple pace calculator for running. Functionallity based on the Cool Running Pace Calculator

from tkinter import *
from tkinter import ttk

METERS = 1
KILOMETERS = 1000

LAPS = 400

FEET = 0.3048
MILES = 1609.344

class PaceCalculator:
	def __init__(self, root):
		root.title("5K Pace Calculator")
	
		mainframe = ttk.Frame(root, padding="3 3 12 12")
		mainframe.grid(column=0, row=0, stick=(N, W, E, S))
	
		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1)
	
		self.time_var = StringVar()
		time_entry = ttk.Entry(mainframe, width=7, textvariable=self.time_var)
		time_entry.grid(column=2, row=1, sticky=(W, E))
	
		self.pace_var = StringVar()
		ttk.Label(mainframe, textvariable=self.pace_var).grid(column=2, row=2, sticky=(W, E))
	
	
		ttk.Label(mainframe, text="5k Time").grid(column=3, row = 1, sticky=W)
		ttk.Label(mainframe, text="Gives a pace of").grid(column=1, row=2)
	
		ttk.Button(mainframe, text="Calculate", command=self.calculate).grid(column=3, row=3, sticky=W)
	
		for child in mainframe.winfo_children():
			child.grid_configure(padx=5, pady=5)
		time_entry.focus()
		root.bind("<Return>", self.calculate)
	
	def calculate(self, *args):
		try:
			minutes = float(self.time_var.get())
	
			min_per_mile = minutes / (5000 * METERS / MILES)		
			seconds = 60 * (min_per_mile % 1)
	
			self.pace_var.set("%d:%3.1f" % (int(min_per_mile), seconds))	
		except ValueError:
			pass



root = Tk()
PaceCalculator(root)
root.mainloop()