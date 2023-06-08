# Using data from alltime-athletics list tracking the yearly
# progression for a runners in a chosen event
# 
# Compare runners based on 1500m, 5000m, 10000m, Half, Full
#
# Create a nice presentation in manim based on the results

import requests
import re
import datetime
from bs4 import BeautifulSoup

Events = ["1500", "5000", "10000", "Half Marathon", "Full Marathon"]

URLS = [
	"http://www.alltime-athletics.com/m_1500ok.htm",
	"http://www.alltime-athletics.com/m_5000ok.htm",
	"http://www.alltime-athletics.com/m_10kok.htm",
	"http://www.alltime-athletics.com/mhmaraok.htm",
	"http://www.alltime-athletics.com/mmaraok.htm"
	]

event_count = len(URLS)

years = {key:[] for key in range(1980,2024)}

event_index = 4


print("Downloading results for " + Events[event_index])

response = requests.get(URLS[event_index])
soup = BeautifulSoup(response.content, "html.parser")
page = soup.find("pre")

perf_list = page.text.split("\n")

country_filter = {}

for t in perf_list[::-1]:
	while t.replace("   ", "  ") != t:
		t = t.replace("   ", "  ")

	# 0 - Index
	# 1 - Time
	# 2 - Name
	# 3 - Country
	# 4 - Birth Year
	# 5 - Place
	# 6 - Location
	# 7 - Date
	line = t.strip().split("  ")

	# Ignore lines that are not data
	if len(line) <= 1:
		continue

	if len(country_filter) and line[3] not in country_filter:
		continue

	# Parse the event time, create time_float
	time_str = line[1]
	if event_index < 3: # 1500,
		time_str = time_str.replace(".",":")
		time_list = time_str.split(":")
		time_float = 60 * int(time_list[0]) + int(time_list[1]) + 0.01 * int(re.sub("[^0-9]", "", time_list[2]))
	elif event_index == 3:
		time_list = time_str.split(":")
		time_float = 60 * int(time_list[0]) + int(re.sub("[^0-9]", "", time_list[1]))
	elif event_index == 4:
		time_list = time_str.split(":")
		time_float = 3600 * int(time_list[0]) + 60 * int(time_list[1]) + int(re.sub("[^0-9]", "", time_list[2]))
	# Parse the event year, create year
	date_list = line[-1].split('.')
	year = int(date_list[2])
	
	if year >= 1980:
		years[year].insert(0, time_float)

print("Working, I guess??")


# Need to manually iterate over dictionary because dictionaries are not guaranteed to preserve key order
for y in range(2000, 2024):
	year_list = years[y]

	disp_list = [''] * 5
	for i in range(0,5):
		event_time = year_list[i]
		disp_list[i] = str(datetime.timedelta(seconds=event_time))[0:7]
	print(f"{y},{disp_list[0]},{disp_list[1]},{disp_list[2]},{disp_list[3]},{disp_list[4]},")


#def is_dominated(candidate, elite):
#	for i in range(0,5):
#		if runner_prs[candidate][i] <= runner_prs[elite][i] and runner_prs[candidate][i] < 10000:
#			return False
#	return True
#
#elites = set()
##elites.add("Kenenisa Bekele")
#
#print("*****************")
#print()
#
#for key in runner_prs.keys():
#	runner_dominated = False
#
#	# Check if it dominates any of the existing elites	
#	# Check if any of the existing elites dominate it
#	for elite in elites.copy():
#		if is_dominated(key, elite):
#			runner_dominated = True
#		if is_dominated(elite, key):
#			elites.remove(elite)
#		
#	if runner_dominated != True:
#		elites.add(key)
#
#sorted_elites = list(elites)
#sorted_elites.sort()
#
#for elite in sorted_elites:
#	disp_list = [''] * 5
#	for i in range(0, event_count):
#		event_time = runner_prs[elite][i]
#		if event_time < 10000:
#			disp_list[i] = str(datetime.timedelta(seconds=event_time))[0:7]
#		else:
#			disp_list[i] = "       "	
#	print(elite + " " * (40 - len(elite)) + str(disp_list))
#
#
#print()
#print("*****************")
#
##for key in runner_prs.keys():
##	print(key + "  " + str(runner_prs[key]))
#	