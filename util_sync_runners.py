# Util library to handle backend data gathering, parsing, and caching from alltime-athletics.com
#
# Data is stored as such:
# (time: float, name: string, country: string, place: string, date: string)

from collections import namedtuple
import time

import requests
import re
import datetime
from bs4 import BeautifulSoup

import sqlite3

Event = namedtuple("Event", "name distance url")

Canonical_Events = [
	Event("1500", 1500, "http://www.alltime-athletics.com/m_1500ok.htm"),
	Event("5000", 5_000, "http://www.alltime-athletics.com/m_5000ok.htm"),
	Event("10000", 10_000, "http://www.alltime-athletics.com/m_10kok.htm"),
	Event("Half Marathon", 21_098, "http://www.alltime-athletics.com/mhmaraok.htm"),
	Event("Marathon", 42_195, "http://www.alltime-athletics.com/mmaraok.htm")
	]

Result = namedtuple("Result", "time name country place date")

# Create/ Load the cache database from a file
# If needed, create the necessary database structure
def build_db(db_path):
	db_connection = sqlite3.connect(db_path)
	cursor = db_connection.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS results(
		result_id INTEGER PRIMARY KEY AUTOINCREMENT,
		valid_until INT, 
		distance INT,
		time REAL,
		name TEXT,
		country TEXT,
		place TEXT,
		date TEXT
	);""")

	return db_connection

# Check if the cached results are still valid.
# If not, clear them from the datatbase
def cache_is_valid(db_connection):
	cursor = db_connection.cursor()
	cached_results = cursor.execute("SELECT valid_until FROM results;", ()).fetchone()
	if cached_results is None or time.time() > cached_results[0]:
		cursor.execute("DELETE FROM results;")
		db_connection.commit()
		return False
	return True

# Get data from alltime-athletics for the given events.
# lifespan denotes how long, in seconds, the cache will stay valid
def get_results(db_connection, events, lifespan):
	time_multipliers = [0.01, 1, 60, 3600]

	cursor = db_connection.cursor()
	for event in events:
		print("Compiling results for " + event.name)

		response = requests.get(event.url)
		soup = BeautifulSoup(response.content, "html.parser")
		page = soup.find("pre")

		runner_list = page.text.split("\n")

		for t in runner_list:
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
			# Not all lines contain birth year, so place, location, date should be reverse indexed
			line = t.strip().split("  ")

			if len(line) <= 1:
				continue

			time_str = line[1]

			# Does time record to seconds or hundreths
			time_offset = 1
			if "." in time_str:
				time_offset = 0

			time_list = time_str.replace(".", ":").split(":")

			time_float = 0.0
			for i, e in enumerate(reversed(time_list)):
				time_float += time_multipliers[i + time_offset] * int(re.sub("[^0-9]", "", e))

			# (time, name, country, place, date)
			r = Result(time_float, line[2], line[3], line[-3], line[-1])

			cursor.execute("INSERT INTO results (valid_until, distance, time, name, country, place, date) VALUES(?, ?, ?, ?, ?, ?, ?);", (time.time() + lifespan, event.distance) + r)		
	db_connection.commit()

def main():
	db_path = 'data/runners/result_cache.db'
	db = build_db(db_path)

	if not cache_is_valid(db):
		print("No valid cache!")
		get_results(db, Canonical_Events, 24*60*60)
	else:
		print("Cache found!!")
	
	db.close()

if __name__ == '__main__':
	main()