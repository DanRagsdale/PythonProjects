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

from runners_sync_data import *

EVENTS = OLYMPIC_EVENTS

rdbc = RunnerDBConnection(RUNNER_DB_PATH)

event_count = len(EVENTS)
elites = set()
runner_prs = {}

for i, e in enumerate(EVENTS):
	print("Parsing results for " + e.name)

	results = rdbc.get_event_results(e)

	for r in results[::-1]:
			
			pr_list = runner_prs.get(r.name, [100000] * event_count)
			pr_list[i] = r.time

			runner_prs[r.name] = pr_list


def is_dominated(candidate, elite):
	for i in range(0,event_count):
		if runner_prs[candidate][i] <= runner_prs[elite][i] and runner_prs[candidate][i] < 10000:
			return False
	return True

print("*****************")
print()

for key in runner_prs.keys():
	runner_dominated = False

	# Check if it dominates any of the existing elites	
	# Check if any of the existing elites dominate it
	for elite in elites.copy():
		if is_dominated(key, elite):
			runner_dominated = True
		if is_dominated(elite, key):
			elites.remove(elite)
		
	if runner_dominated != True:
		elites.add(key)

sorted_elites = list(elites)
sorted_elites.sort()

for elite in sorted_elites:
	disp_list = [''] * event_count
	for i in range(0, event_count):
		event_time = runner_prs[elite][i]
		if event_time < 10000:
			disp_list[i] = str(datetime.timedelta(seconds=event_time))[0:7]
		else:
			disp_list[i] = "       "	
	print(elite + " " * (40 - len(elite)) + str(disp_list))


print()
print("*****************")

#for key in runner_prs.keys():
#	print(key + "  " + str(runner_prs[key]))
	