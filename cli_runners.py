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

elites = set()
runner_prs = {}


for index in range(0, event_count):
	print("Compiling results for " + Events[index])

	response = requests.get(URLS[index])
	soup = BeautifulSoup(response.content, "html.parser")
	page = soup.find("pre")

	runner_list = page.text.split("\n")

	for t in runner_list[::-1]:
		while t.replace("   ", "  ") != t:
			t = t.replace("   ", "  ")

		line = t.strip().split("  ")

		if len(line) > 1:
			time_str = line[1]
			if index < 3:
				time_str = time_str.replace(".",":")
				time_list = time_str.split(":")
				time_float = 60 * int(time_list[0]) + int(time_list[1]) + 0.01 * int(re.sub("[^0-9]", "", time_list[2]))
			elif index == 3:
				time_list = time_str.split(":")
				time_float = 60 * int(time_list[0]) + int(re.sub("[^0-9]", "", time_list[1]))
			elif index == 4:
				time_list = time_str.split(":")
				time_float = 3600 * int(time_list[0]) + 60 * int(time_list[1]) + int(re.sub("[^0-9]", "", time_list[2]))

			pr_list = runner_prs.get(line[2], [100000] * 5)
			pr_list[index] = time_float

			runner_prs[line[2]] = pr_list


def is_dominated(candidate, elite):
	for i in range(0,5):
		if runner_prs[candidate][i] <= runner_prs[elite][i] and runner_prs[candidate][i] < 10000:
			return False
	return True

#elites.add("Kenenisa Bekele")

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
	disp_list = [''] * 5
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
	