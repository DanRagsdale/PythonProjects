# Using data from alltime-athletics list tracking the yearly
# progression for a runners in a chosen event
# 
# Compare runners based on 1500m, 5000m, 10000m, Half, Full

import datetime

import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

from tkinter import *
from tkinter import ttk

from runners_sync_data import *

# User Variables

country_filter = {} # Only count performances from the specified country, e.g. 'USA'
ignore_losers = False # Only count the winning performance from each race. Helps elimate skew frow a single fast race in a year

# Return a dictionary of lists of all of the best times for the given years, in order
def get_year_lists(event, years):
	year_lists = {key:[] for key in years}

	rdbc = RunnerDBConnection(RUNNER_DB_PATH)
	results = rdbc.get_event_results(event)

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

# Return a list of the best times in each year	
def get_yearly_bests(year_lists, years):
	best_times = []
	
	for year in years:
		year_list = year_lists[year]

		disp_list = [f"{str(datetime.timedelta(seconds=t))[0:7]}, " for t in year_list]

		#print(f"{year},  {disp_list[0:10]}")

		best_times.append(year_list[0])

	return best_times

if __name__ == '__main__':
	event = EVENT_5000
	years = range(1980, 2024)

	year_lists = get_year_lists(event, years)
	best_times = get_yearly_bests(year_lists, years)
	
	# GUI code	
	window = Tk()

	window.title("Runner Progressions by year")
	window.geometry('600x600')
	# test_button = Button(master = window, command = test_plot, height = 2, width = 10, text = "Plot!")	
	# test_button.pack()
			
	fig = Figure(figsize = (5, 5), dpi = 100)

	plot1 = fig.add_subplot(111)
	plot1.plot(years, best_times)
	plot1.yaxis.set_major_formatter(lambda t, _: str(datetime.timedelta(seconds=t)))
	plot1.set(xlabel="Year", ylabel="Time", title=f"{event.name} progression by year")

	canvas = FigureCanvasTkAgg(fig, master = window)
	canvas.draw()

	canvas.get_tk_widget().pack()

	toolbar = NavigationToolbar2Tk(canvas, window)
	canvas.get_tk_widget().pack()

	window.mainloop()