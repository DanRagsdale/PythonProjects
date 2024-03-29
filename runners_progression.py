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
#country_filter = set() # Only count performances from the specified country, e.g. 'USA'
YEARS = range(1980, 2024)
EVENTS = CANONICAL_EVENTS

# Return a dictionary of lists of all of the best times for the given years, in order
rdbc = RunnerDBConnection(RUNNER_DB_PATH)
def get_year_lists(sex, event, years, country_filter=None):
	year_lists = {key:[] for key in years}

	results = rdbc.get_event_results(sex, event)

	for r in results[::-1]:
		if country_filter and r.country not in country_filter:
			continue

		# Parse the event year, create year
		date_list = r.date.split('.')
		year = int(date_list[2])

		if year in years:
			year_lists[year].insert(0, r.time)
	
	return year_lists

# Return a dictionary of the best times in each year	
def get_yearly_bests(year_lists, years, nth_best = 0):
	best_times = {}
	
	for year in years:
		year_list = year_lists[year]

		if len(year_list) > nth_best:
			best_times[year] = year_list[nth_best]

	return best_times

class progression_gui(tk.Frame):
	def __init__(self, window = None):
		tk.Frame.__init__(self, window)

		# GUI code	
		window.title("runner progressions by year")
		window.geometry('600x600')

		# User Input
		frame = Frame(window)
		frame.pack()

		sex_box = ttk.Combobox(frame, state='readonly')
		sex_box['values'] = [s.name for s in SEXES]
		sex_box.current(0)
		sex_box.grid(column=0, row=0, padx=3)

		test_box = ttk.Combobox(frame, state='readonly')
		test_box['values'] = [e.name for e in EVENTS] 
		test_box.current(0)
		test_box.grid(column=1, row=0, padx=3)
		
		test_box.bind('<<ComboboxSelected>>', lambda x: self.draw_progression(x, SEXES[sex_box.current()], EVENTS[test_box.current()])) 
		sex_box.bind('<<ComboboxSelected>>', lambda x: self.draw_progression(x, SEXES[sex_box.current()], EVENTS[test_box.current()])) 

		# Matplotlib GUI
		self.fig = Figure(figsize = (5, 5), dpi = 100)

		self.canvas = FigureCanvasTkAgg(self.fig, master=window)
		self.canvas.draw_idle()

		toolbar = NavigationToolbar2Tk(self.canvas, window)
		toolbar.update()
		self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

		self.draw_progression(None, MALE, EVENT_1500)

		window.mainloop()


	def draw_progression(self, _, sex, event):
		year_lists = get_year_lists(sex, event, YEARS)
		
		best_times = get_yearly_bests(year_lists, YEARS)
		fifth_times = get_yearly_bests(year_lists, YEARS, nth_best=4)

		self.fig.clear()		
		plot1 = self.fig.add_subplot(111)

		plot1.plot(best_times.keys(), best_times.values())
		plot1.plot(fifth_times.keys(), fifth_times.values())
		
		plot1.yaxis.set_major_formatter(lambda t, _: str(datetime.timedelta(seconds=t)))
		plot1.set(xlabel="Year", ylabel="Time", title=f"{sex.possesive} {event.name} progression by year")

		self.canvas.draw()		


if __name__ == '__main__':
	window = Tk()
	gui = progression_gui(window = window)