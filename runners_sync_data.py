# Util library to handle backend data gathering, parsing, and caching from alltime-athletics.com
#
# Data is stored as such:
# (distance: int, time: float, name: string, country: string, place: string, date: string)

from typing import NamedTuple
import time
import itertools

import requests
import re
import datetime
from bs4 import BeautifulSoup

import sqlite3

class Event(NamedTuple):
	name: str
	distance: int
	urls: tuple[str, str]	

class Result(NamedTuple):
	time: float
	name: str
	country: str
	place: str
	date: str

class Sex(NamedTuple):
	name: str
	index: int
	possesive: str

RUNNER_DB_PATH = 'data/runners/result_cache.db'

# Sexes for all of the events
MALE = Sex('Male', 0, "Men's")
FEMALE = Sex('Female', 1, "Women's")

SEXES = [MALE, FEMALE]

EVENT_1500 = Event("1500m", 1500, ("http://www.alltime-athletics.com/m_1500ok.htm", "http://www.alltime-athletics.com/w_1500ok.htm"))
EVENT_5000 = Event("5000m", 5_000, ("http://www.alltime-athletics.com/m_5000ok.htm", "http://www.alltime-athletics.com/w_5000ok.htm"))
EVENT_10000 = Event("10000m", 10_000, ("http://www.alltime-athletics.com/m_10kok.htm", "http://www.alltime-athletics.com/w_10kok.htm"))
EVENT_HALF = Event("Half Marathon", 21_098, ("http://www.alltime-athletics.com/mhmaraok.htm", "http://www.alltime-athletics.com/whmaraok.htm"))
EVENT_FULL = Event("Marathon", 42_195, ("http://www.alltime-athletics.com/mmaraok.htm", "http://www.alltime-athletics.com/wmaraok.htm"))

# The events which, by default, this util will download
CANONICAL_EVENTS = [
	EVENT_1500,
	EVENT_5000,
	EVENT_10000,
	EVENT_HALF,
	EVENT_FULL,
	]

OLYMPIC_EVENTS = [
	EVENT_1500,
	EVENT_5000,
	EVENT_10000,
	EVENT_FULL,
]

# Create/ Load the cache database from a file
# If needed, create the necessary database structure
def build_db(db_path):
	db_connection = sqlite3.connect(db_path)

	db_connection.execute("""CREATE TABLE IF NOT EXISTS results(
		result_id INTEGER PRIMARY KEY AUTOINCREMENT,
		valid_until INT, 
		sex INT,
		distance INT,
		time REAL,
		name TEXT,
		country TEXT,
		place TEXT,
		date TEXT
	);""")
	db_connection.commit()

	return db_connection


NORMAL_CACHE = 0
IGNORE_CACHE_TIMEOUT = 1 # Use cached results, even if they are expired. Useful for offline testing
FORCE_REFRESH = 2 # Always redownload results, even if they are still valid.

CACHE_STATE = IGNORE_CACHE_TIMEOUT

# Check if the cached results are still valid.
# If not, clear them from the datatbase
def cache_is_valid(db_connection):
	cached_results = db_connection.execute("SELECT valid_until FROM results;", ()).fetchone()
	if cached_results is None:
		return False	
	if CACHE_STATE == FORCE_REFRESH:
		db_connection.execute("DELETE FROM results;")
		db_connection.commit()
		return False
	if CACHE_STATE == IGNORE_CACHE_TIMEOUT:
		return True
	if time.time() > cached_results[0]:
		db_connection.execute("DELETE FROM results;")
		db_connection.commit()
		return False
	return True

# Get data from alltime-athletics for the given events.
# lifespan denotes how long, in seconds, the cache will stay valid
def download_results(db_connection, events, lifespan):
	time_multipliers = [0.01, 1, 60, 3600]

	for sex, event in itertools.product(SEXES, events):
		print("Compiling results for " + event.name + " for " + sex.possesive)

		response = requests.get(event.urls[sex.index])
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

			db_connection.execute("INSERT INTO results (valid_until, sex, distance, time, name, country, place, date) VALUES(?, ?, ?, ?, ?, ?, ?, ?);",
				(time.time() + lifespan, sex.index, event.distance) + r)		
	db_connection.commit()

# The primary mecahnism for accessing runner data
class RunnerDBConnection:
	def __init__(self, db_path):
		self.db_connection = build_db(db_path)

		if not cache_is_valid(self.db_connection):
			print("No valid cache!")
			download_results(self.db_connection, CANONICAL_EVENTS, 3*24*60*60)
		else:
			print("Cache found!!")
		
		self.cursor = self.db_connection.cursor()

	# Get all of the results for the specified event, ordered from best to worst
	def get_event_results(self, sex, event):
		raw_results = self.db_connection.execute("SELECT time, name, country, place, date FROM results WHERE sex = ? AND distance = ? ORDER BY time ASC;", (sex.index, event.distance)).fetchall()
		return [Result(r[0], r[1], r[2], r[3], r[4]) for r in raw_results]

# This file should primarily be used as a library.
# This main function is simply for testing and debugging
def main():
	rdbc = RunnerDBConnection(RUNNER_DB_PATH)
	print(rdbc.get_event_results(MALE, EVENT_1500)[0:10])

if __name__ == '__main__':
	main()