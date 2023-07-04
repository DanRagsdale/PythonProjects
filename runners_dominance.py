# Using data from alltime-athletics determine all of the pareto optimal distance runners
# Compare runners based on 1500m, 5000m, 10000m, Half, Full
#
# Create a nice presentation in manim based on the results

# Algorithm for determing efficiency:

# We know we have finished when all other possible runners are dominated
# Could find a "Floor" runner like Mo or Bekele and conclude once we have checked everyone with at least 1 PR faster than them
# 	This seems like the obvious/ optimal solution for this specific problem, but may not generalize
# 	After thinking about it, you probably have to do something like this

# For a "Hard" version of the problem, only consider 3 adjacent events for each runner. E.g. only look at Bekele's 1500m, 5000m, 10000m
#	Would need to find a "floor" runner for each specific set of events

import datetime
from io import StringIO
from dataclasses import dataclass

import tkinter as tk
from tkinter import *
from tkinter import ttk

from runners_sync_data import *


EVENTS = OLYMPIC_EVENTS

@dataclass
class Runner:
	name: str
	bests: dict

def is_dominated(candidate, elite):
	for e in EVENTS:
		# Return false iff there is an event both have run, and if candidate is at least as fast
		# If candidate has not run the event, then continue checking other events
		# If elite has not run the event and the candidate has, canditate is not dominated so return False
		# Comparisons with NaN always return False
		if candidate.bests.get(e, float('nan')) <= elite.bests.get(e, float('inf')):
			return False
	return True

rdbc = RunnerDBConnection(RUNNER_DB_PATH)
def get_elites(sex):
	elites = []
	runners = {}
	
	for e in EVENTS:
		results = rdbc.get_event_results(sex, e)

		for r in results[::-1]:
				runner = runners.get(r.name, Runner(r.name, {}))
				runner.bests[e] = r.time
				runners[r.name] = runner

	for candidate in runners.values():
		runner_dominated = False

		# Check if it dominates any of the existing elites	
		# Check if any of the existing elites dominate it
		for elite in elites.copy():
			if is_dominated(candidate, elite):
				runner_dominated = True
			if is_dominated(elite, candidate):
				elites.remove(elite)

		if runner_dominated != True:
			elites.append(candidate)

	elites.sort(key=lambda x: x.name)
	return elites

class dominance_gui(tk.Frame):
	def __init__(self, window):
		tk.Frame.__init__(self, window)
		
		# GUI init	
		window.title("The True Elite")
		window.geometry('600x600')
		
		# User input	
		sex_box = ttk.Combobox(window, state='readonly')
		sex_box['values'] = [s.name for s in SEXES]
		sex_box.current(0)
		sex_box.grid(column=0, row=0, padx=3)

		sex_box.bind('<<ComboboxSelected>>', lambda x: self.draw_elites(SEXES[sex_box.current()])) 

		# Output Display
		self.output_names = StringVar()
		names = ttk.Label(window, textvariable=self.output_names)
		names.grid(column=0, row=1, padx=5)

		self.output_events = {}
		for i, e in enumerate(EVENTS):
			outputContent = StringVar()
			self.output_events[e] = outputContent
			output = ttk.Label(window, textvariable=outputContent)
			output.grid(column=(i+1), row = 1, padx=5)

		self.draw_elites(MALE)
	
		window.mainloop()

	def draw_elites(self, sex):
		elites = get_elites(sex)

		def init_stringio(initial_value):
			output = StringIO(initial_value)
			output.seek(0, 2)
			return output

		name_buffer = init_stringio('\n\n')
		event_buffers = {event:init_stringio(f"{event.name}\n\n") for event in EVENTS}

		for elite in elites:
			name_buffer.write(f"{elite.name}\n")

			for e in EVENTS:
				if e in elite.bests:
					event_buffers[e].write(f"{str(datetime.timedelta(seconds=elite.bests[e]))[0:7]}\n")
				else:
					event_buffers[e].write("\n")
				
		self.output_names.set(name_buffer.getvalue())	
		for e in EVENTS:
			self.output_events[e].set(event_buffers[e].getvalue())

if __name__ == '__main__':
	window = Tk()
	gui = dominance_gui(window)
	