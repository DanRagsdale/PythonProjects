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

import tkinter as tk
from tkinter import *
from tkinter import ttk

from typing import NamedTuple
from dataclasses import dataclass

from runners_sync_data import *


EVENTS = OLYMPIC_EVENTS
rdbc = RunnerDBConnection(RUNNER_DB_PATH)

@dataclass
class Runner:
	name: str
	bests: dict


event_count = len(EVENTS)
elites = []
runners = {}

def is_dominated(candidate, elite):
	for e in EVENTS:
		if e in candidate.bests and candidate.bests[e] <= elite.bests.get(e, 10000):
		#if runner_prs[candidate][i] <= runner_prs[elite][i] and runner_prs[candidate][i] < 10000:
			return False
	return True

for e in EVENTS:
	print("Parsing results for " + e.name)

	results = rdbc.get_event_results(FEMALE, e)

	for r in results[::-1]:
			runner = runners.get(r.name, Runner(r.name, {}))
			runner.bests[e] = r.time
			runners[r.name] = runner

print("*****************")
print()

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

event_count = len(EVENTS)

for elite in elites:
	disp_list = [''] * event_count
	for i, e in enumerate(EVENTS):
		event_time = elite.bests.get(e, 10000)
		if event_time < 10000:
			disp_list[i] = str(datetime.timedelta(seconds=event_time))[0:7]
		else:
			disp_list[i] = "       "	
	print(elite.name + " " * (40 - len(elite.name)) + str(disp_list))


print()
print("*****************")


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
		#sex_box.grid(column=0, row=0, padx=3)
		sex_box.pack()

		sex_box.bind('<<ComboboxSelected>>', lambda x: self.draw_elites(SEXES[sex_box.current()])) 

		# Output Display
		self.outputContent = StringVar()

		output = ttk.Label(window)
		output['textvariable'] = self.outputContent
		output.pack()

		window.mainloop()

	def draw_elites(self, sex):
		self.outputContent.set(sex.name)

if __name__ == '__main__':
	window = Tk()
	gui = dominance_gui(window)
	