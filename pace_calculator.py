# Simple pace calculator for running. Functionallity based on the Cool Running Pace Calculator

from re import I
from tkinter import *
from tkinter import ttk

METERS = 1
KILOMETERS = 1000

LAPS = 400

FEET = 0.3048
MILES = 1609.344

SIXTEEN = 1600

MARATHONS = 42195

DISTANCES = ["Meters", "Kilometers", "Feet", "Miles", "Laps", "Marathons"]
DISTANCE_VALUES = [METERS, KILOMETERS, FEET, MILES, LAPS, MARATHONS]

PACES = ["Kilometer", "Mile", "1600m", "Lap"]
PACE_VALUES = [KILOMETERS, MILES, SIXTEEN, LAPS]

def s_float(s):
	s = s.strip()
	return float(s) if s else 0

class PaceCalculator:
	def __init__(self, root):
		root.title("5K Pace Calculator")
	
		mainframe = ttk.Frame(root, padding="3 3 12 12")
		mainframe.grid(column=0, row=0, stick=(N, W, E, S))
	
		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1)


		ttk.Label(mainframe, text="Simple Pace Calculator").grid(column=0, row=0, columnspan=3, stick=(W, E))


	# Time
		ttk.Label(mainframe, text="Time").grid(column=0, row=1)

		time_frame = ttk.Frame(mainframe)
		time_frame.grid(column=1, row=1, sticky=(N, E, S, W))

		ttk.Label(time_frame, text="Hours").grid(column=0, row=0)
		self.hour_var = StringVar()
		hour_entry = ttk.Entry(time_frame, width=7, textvariable=self.hour_var)
		hour_entry.grid(column=0, row=1, sticky=(W, E), padx=5)
		
		ttk.Label(time_frame, text="Mins").grid(column=1, row=0)
		self.min_var = StringVar()
		ttk.Entry(time_frame, width=7, textvariable=self.min_var).grid(column=1, row=1, sticky=(W, E), padx=5)
		
		ttk.Label(time_frame, text="Secs").grid(column=2, row=0)
		self.sec_var = StringVar()
		ttk.Entry(time_frame, width=7, textvariable=self.sec_var).grid(column=2, row=1, sticky=(W, E), padx=5)

		ttk.Button(mainframe, text="Calculate Time", command=self.calc_time).grid(column=2, row=1)


	#Distance
		ttk.Label(mainframe, text="Distance").grid(column=0, row=2)

		dist_frame = ttk.Frame(mainframe)
		dist_frame.grid(column=1, row=2, sticky=(N, E, S, W))

		self.dist_var = StringVar()
		dist_entry = ttk.Entry(dist_frame, width=7, textvariable=self.dist_var)
		dist_entry.grid(column=0, row=0, sticky=(W, E), padx=5)

		self.dist_cb = ttk.Combobox(dist_frame, values=DISTANCES, state="readonly")
		self.dist_cb.current(1)
		self.dist_cb.grid(column=1, row=0, padx=5)

		ttk.Button(mainframe, text="Calculate Distance", command=self.calc_dist).grid(column=2, row=2)

	#Pace
		ttk.Label(mainframe, text="Pace").grid(column=0, row=3)

		pace_frame = ttk.Frame(mainframe)
		pace_frame.grid(column=1, row=3, sticky=(N, E, S, W))

		ttk.Label(pace_frame, text="Mins").grid(column=0, row=0)		
		self.pmin_var = StringVar()
		ttk.Entry(pace_frame, width=7, textvariable=self.pmin_var).grid(column=0, row=1, padx=5)
		
		ttk.Label(pace_frame, text="Secs").grid(column=1, row=0)		
		self.psec_var = StringVar()
		ttk.Entry(pace_frame, width=7, textvariable=self.psec_var).grid(column=1, row=1, sticky=(W, E), padx=5)

		ttk.Label(pace_frame, text="Per").grid(column=2, row=0)
		self.pace_cb = ttk.Combobox(pace_frame, values=PACES, state="readonly")
		self.pace_cb.current(1)
		self.pace_cb.grid(column=2, row=1, padx=5)

		ttk.Button(mainframe, text="Calculate Pace", command=self.calc_pace).grid(column=2, row=3)


		for child in mainframe.winfo_children():
			child.grid_configure(padx=5, pady=5)
		hour_entry.focus()

	def calc_time(self, *args):
		try:
			dist = s_float(self.dist_var.get()) * DISTANCE_VALUES[self.dist_cb.current()]
			pace = (s_float(self.pmin_var.get()) * 60 + s_float(self.psec_var.get())) / PACE_VALUES[self.pace_cb.current()] # pace in seconds / meter
			time = dist * pace

			self.hour_var.set(int(time / 3600))
			self.min_var.set(int((time % 3600) / 60))
			self.sec_var.set(round(time % 60, 2))
		except ValueError:
			pass	
	
	def calc_dist(self, *args):
		try:
			time = s_float(self.hour_var.get()) * 3600 + s_float(self.min_var.get()) * 60 + s_float(self.sec_var.get())
			pace = (s_float(self.pmin_var.get()) * 60 + s_float(self.psec_var.get())) / PACE_VALUES[self.pace_cb.current()] # pace in seconds / meter

			dist = time / pace

			self.dist_var.set(round(dist / DISTANCE_VALUES[self.dist_cb.current()], 2))
		except ValueError:
			pass

	def calc_pace(self, *args):
		try:
			time = s_float(self.hour_var.get()) * 3600 + s_float(self.min_var.get()) * 60 + s_float(self.sec_var.get())
			dist = s_float(self.dist_var.get()) * DISTANCE_VALUES[self.dist_cb.current()]

			pace = round(time / dist * PACE_VALUES[self.pace_cb.current()],2)

			self.pmin_var.set(int(pace / 60))
			self.psec_var.set(round(pace % 60, 2))
			
		except ValueError:
			pass


root = Tk()
PaceCalculator(root)
root.mainloop()