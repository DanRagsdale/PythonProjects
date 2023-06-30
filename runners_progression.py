# Using data from alltime-athletics list tracking the yearly
# progression for a runners in a chosen event
# 
# Compare runners based on 1500m, 5000m, 10000m, Half, Full

import datetime

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from util_sync_runners import *

# User Variables

event = EVENT_HALF

country_filter = {} # Only count performances from the specified country, e.g. 'USA'
ignore_losers = False # Only count the winning performance from each race. Helps elimate skew frow a single fast race in a year

years = {key:[] for key in range(1980,2024)}

# Code
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
	
	if year >= 1980:
		years[year].insert(0, r.time)


# Need to manually iterate over dictionary because dictionaries are not guaranteed to preserve key order
best_times = []
fifth_times = []
tenth_times = []

output_range = range(2000, 2024)
for year in output_range:
	year_list = years[year]

	disp_list = [f"{str(datetime.timedelta(seconds=t))[0:7]}, " for t in year_list]
	
	#print(f"{year},  {disp_list[0:10]}")

	best_times.append(year_list[0])
	fifth_times.append(year_list[4])
	tenth_times.append(year_list[9])

fig, ax = plt.subplots()

ax.plot(output_range, best_times)
ax.plot(output_range, fifth_times)
ax.plot(output_range, tenth_times)
ax.yaxis.set_major_formatter(lambda t, _: str(datetime.timedelta(seconds=t)))

ax.set(xlabel="Year", ylabel="Time", title=f"{event.name} progression by year")

plt.show()