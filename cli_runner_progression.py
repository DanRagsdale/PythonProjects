# Using data from alltime-athletics list tracking the yearly
# progression for a runners in a chosen event
# 
# Compare runners based on 1500m, 5000m, 10000m, Half, Full

import datetime

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from util_sync_runners import *

country_filter = {} # Only count performances from the specified country, e.g. 'USA'
ignore_losers = True # Only count the winning performance from each race. Helps elimate skew frow a single fast race in a year

years = {key:[] for key in range(1980,2024)}

# New code
rdbc = RunnerDBConnection(RUNNER_DB_PATH)
results = rdbc.get_event_results(EVENT_1500)

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
for y in range(2000, 2024):
	year_list = years[y]

	disp_list = [''] * 5
	for i in range(0,5):
		event_time = year_list[i]
		disp_list[i] = str(datetime.timedelta(seconds=event_time))[0:7]
	print(f"{y},{disp_list[0]},{disp_list[1]},{disp_list[2]},{disp_list[3]},{disp_list[4]},")

fig, ax = plt.subplots()
ax.plot([1,2,3,8], [1,4,2,3])

plt.show()