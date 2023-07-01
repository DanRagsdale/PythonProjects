# Using data from alltime-athletics list tracking the yearly
# progression for a runners in a chosen event
# 
# Compare runners based on 1500m, 5000m, 10000m, Half, Full

import datetime

import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

import tkinter as tk

from tkinter import *
from tkinter import ttk

from runners_sync_data import *

# User Variables

country_filter = {} # Only count performances from the specified country, e.g. 'USA'
ignore_losers = False # Only count the winning performance from each race. Helps elimate skew frow a single fast race in a year

# Return a dictionary of lists of all of the best times for the given years, in order
def get_year_lists(sex, event, years):
	year_lists = {key:[] for key in years}

	rdbc = RunnerDBConnection(RUNNER_DB_PATH)
	results = rdbc.get_event_results(sex, event)

	for r in results[::-1]:
		if len(country_filter) and r.country not in country_filter:
			continue

		if ignore_losers and (not str.isdigit(r.place) or int(r.place) > 1):
			continue

		# Parse the event year, create year
		date_list = r.date.split('.')
		year = int(date_list[2])

		if year in years:
			year_lists[year].insert(0, r.time)
	
	return year_lists

# Return a dictionary of the best times in each year	
def get_yearly_bests(year_lists, years):
	best_times = {}
	
	for year in years:
		year_list = year_lists[year]

		disp_list = [f"{str(datetime.timedelta(seconds=t))[0:7]}, " for t in year_list]

		#print(f"{year},  {disp_list[0:10]}")

		if len(year_list) > 0:
			best_times[year] = year_list[0]

	return best_times

class progression_gui(tk.Frame):
	def __init__(self, window = None):
		tk.Frame.__init__(self, window)

		# GUI code	
		window.title("runner progressions by year")
		window.geometry('600x600')
		#test_button = Button(master = window, command = test_command, height = 2, width = 10, text = "Plot!")	
		#test_button.pack()

		frame = Frame(window)
		frame.pack()

		self.sex_box = ttk.Combobox(frame, state='readonly')
		self.sex_box['values'] = ['Male', 'Female']
		self.sex_box.current(0)
		self.sex_box.grid(column=0, row=0, padx=3)
		self.sex_box.bind('<<ComboboxSelected>>', self.draw_progression) 

		self.test_box = ttk.Combobox(frame, state='readonly')
		self.test_box['values'] = [e.name for e in CANONICAL_EVENTS] 
		self.test_box.current(0)
		self.test_box.bind('<<ComboboxSelected>>', self.draw_progression) 
		self.test_box.grid(column=1, row=0, padx=3)


		self.fig = Figure(figsize = (5, 5), dpi = 100)

		self.canvas = FigureCanvasTkAgg(self.fig, master=window)
		self.canvas.draw_idle()

		toolbar = NavigationToolbar2Tk(self.canvas, window)
		toolbar.update()
		self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

		self.draw_progression(None)

		window.mainloop()


	def draw_progression(self, _):
		event = CANONICAL_EVENTS[self.test_box.current()]
		years = range(1960, 2024)
		
		year_lists = get_year_lists(self.sex_box.current(), event, years)
		best_times = get_yearly_bests(year_lists, years)

		self.fig.clear()		
		plot1 = self.fig.add_subplot(111)

		plot1.plot(best_times.keys(), best_times.values())
		plot1.yaxis.set_major_formatter(lambda t, _: str(datetime.timedelta(seconds=t)))
		plot1.set(xlabel="Year", ylabel="Time", title=f"{event.name} progression by year")

		self.canvas.draw()		


if __name__ == '__main__':
	window = Tk()
	gui = progression_gui(window = window)