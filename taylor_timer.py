import requests
import base64
import json
import random
import bisect
import typing

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from urllib.parse import quote
from pytimeparse.timeparse import timeparse

import sqlite3
import time


class Track(typing.NamedTuple): 
	id: str
	name: str
	length: int
	uri: str
	explicit: bool

# Fetch the app info from a hidden file
# Use this to generate an authorization token for the spotify api
def get_token():
	client_info_loc = '/home/daniel/Development/tokens/SpotifyIDs.json'

	with open(client_info_loc, 'r') as auth_file:
		auth_json = json.loads(auth_file.read())

		client_id = auth_json['client_id']
		client_secret = auth_json['client_secret']


	auth_url = 'https://accounts.spotify.com/api/token'
	header_obj = { 
		'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode('ascii')).decode('ascii'),
		'Content-Type': 'application/x-www-form-urlencoded',
	}
	data_obj = 'grant_type=client_credentials'

	response = requests.post(auth_url, headers = header_obj, data = data_obj)

	if response.status_code != 200:
		exit()

	token = response.json()['access_token']
	return token

def get_artist_id(token, search_string):
	query = quote(search_string)
	search_url = f'https://api.spotify.com/v1/search?q={query}&type=artist&limit=1'
	header_obj = {
		'Authorization': 'Authorization: Bearer ' + token
	}

	response = requests.get(search_url, headers = header_obj)

	return response.json()['artists']['items'][0]['id']

# Get a list of all albums for a given artist
def get_albums(token, artist_id):
	albums = []

	offset = 0
	while True:
		artists_album_url = f'https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album&market=US&limit=50&offset={offset}'
		header_obj = {
			'Authorization': 'Authorization: Bearer ' + token
		}

		response = requests.get(artists_album_url, headers = header_obj)

		response_albums = response.json()['items']
		for album in response_albums:
			name = album['name']
			if "karaoke" not in name.lower():
				albums.append(album['id'])

		if offset + 50 > response.json()['total']:
			break
		offset += 50
	return albums

# Iterate through all the albums and get a list of all tracks from the provided albums
def get_tracks(token, albums):
	tracks = []

	for album_id in albums:
		album_tracks_url = 'https://api.spotify.com/v1/albums/' + str(album_id) + '/tracks?limit=50'	
		header_obj = {
			'Authorization': 'Authorization: Bearer ' + token
		}

		response = requests.get(album_tracks_url, headers = header_obj)
		response_tracks = response.json()['items']

		for track in response_tracks:
			name = track['name']

			if 'commentary' not in name.lower() and 'voice memo' not in name.lower():
				test_track = Track(
					id = track['id'],
					name = track['name'],
					length = track['duration_ms'],
					uri = track['uri'],
					explicit = track['explicit'],
				)
				
				should_add = True
				for i, t in enumerate(tracks):
					if t.name == test_track.name and (int(t.explicit) >= int(test_track.explicit)):
						should_add = False
						break
					elif t.name == test_track.name:
						tracks[i] = test_track
						should_add = False
						break

				if should_add:
					tracks.append(test_track)
	return tracks

def track_len(track):
	return track.length

# Get the difference in duration between the test_list and the target_time
def playlist_delta(target_time, test_list):
	test_len = sum([track.length for track in test_list])
	return abs(target_time - test_len)


# Determine which tracks can be combined to form a correct partition
def find_playlist(tracks, target_time):
	print()

	tracks.sort(key=track_len)

	track_count = len(tracks)
	med_len = (tracks[track_count // 2]).length

	tracks_needed = max(1, target_time // med_len)
	print(f"Looking for a combination of {tracks_needed} tracks")

	# Try every combination of n tracks in a pseudo random order
	# Return early if a given combination has a total length within an acceptable threshold

	# 10007 is prime. Assuming len(tracks) is less than 10007, then 10007^n is coprime to len(tracks)^n
	# Therefore this will step through all the combinations of songs in pseudo-random order
	random.shuffle(tracks)

	increment = 10_007**tracks_needed
	track_space = track_count**tracks_needed

	test_index = 0

	playlist_tests = []

	for i in range(min(10_000, track_space)):
		test_list	= []
		working_val = test_index
		for t in range(tracks_needed):
			test_list.append(tracks[working_val % track_count])
			working_val //= track_count

		if playlist_delta(target_time, test_list) < 1000:
			print(f"Completed in {i} iterations")
			return test_list

		playlist_tests.append(test_list)
		test_index = (test_index + increment) % track_space

	# Fallback if a perfect match is not found
	print("Failed to find exact playlist. Returning best possible result.")
	best_index = 0
	best_delta = 100_000
	for i, t in enumerate(playlist_tests):
		test_delta = playlist_delta(target_time, t) 
		if test_delta < best_delta:
			best_index = i
			best_delta = test_delta
	return playlist_tests[best_index]

class TimerWindow(Gtk.Window):
	def __init__(self, token, db_path):
		super().__init__(title="Hello World!")

		self.token = token
		self.build_gui()

		self.db_connection = sqlite3.connect(db_path)
		self.cursor = self.db_connection.cursor()

		self.cursor.execute("""CREATE TABLE IF NOT EXISTS artists(
			artist_id TEXT PRIMARY KEY,
			artist_name TEXT,
			timestamp INT
		);""")

		self.cursor.execute("""CREATE TABLE IF NOT EXISTS tracks(
			track_id TEXT PRIMARY KEY,
			artist_id TEXT NOT NULL,
			track_name TEXT NOT NULL,
			track_len INTEGER NOT NULL,
			track_uri TEXT NOT NULL,

			FOREIGN KEY(artist_id) REFERENCES artists(artist_id)
		);""")

	def generate_playlist(self, widget):
		target_time = timeparse(self.time_entry.get_text())
		if target_time is None:
			print("Please enter a valid time!")
			return

		# Check if the tracks for the artist have been cached. If not, get them from the Spotify API
		artist_name = self.artist_entry.get_text().lower()
		cur_time = int(time.time())

		cached_artist = self.cursor.execute(f"SELECT artist_id, timestamp FROM artists WHERE artist_name = '{artist_name}';").fetchone()
		if cached_artist is None or (cur_time - cached_artist[1] > 300):
			print("Getting new Data!!")
			print(cached_artist)
		
			artist_id = get_artist_id(self.token, artist_name)
			self.cursor.execute(f"INSERT OR REPLACE INTO artists VALUES('{artist_id}', '{artist_name}', {cur_time})")		
			
			albums = get_albums(self.token, artist_id)
			tracks = get_tracks(self.token, albums)

			track_data = [(t.id, artist_id, t.name, t.length, t.uri) for t in tracks]
			self.cursor.executemany(f"INSERT OR REPLACE INTO tracks VALUES(?, ?, ?, ?, ?)", track_data)
			self.db_connection.commit()
		else:
			print("Valid cache found!")
			raw_tracks = self.cursor.execute(f"SELECT track_id, track_name, track_len, track_uri FROM tracks WHERE artist_id='{cached_artist[0]}'").fetchall()
			tracks = [Track(id=t[0], name=t[1], length=t[2], uri=t[3], explicit=True) for t in raw_tracks]

		track_list = find_playlist(tracks, target_time*1000)

		disp_string = '\n'.join(track.name for track in track_list)
		self.output_buffer.set_text(disp_string)

	def build_gui(self):
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, margin=6)
		self.add(hbox)

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

		self.button = Gtk.Button(label="Generate Playlist")
		self.button.connect('clicked', self.generate_playlist)
		vbox.pack_start(self.button, False, False, 0)

		self.artist_entry = Gtk.Entry()
		self.artist_entry.set_text("Taylor Swift")
		self.artist_entry.set_placeholder_text("Enter an Artist")
		vbox.pack_start(self.artist_entry, False, False, 0)

		self.time_entry = Gtk.Entry()
		self.time_entry.set_text("10:00")
		self.time_entry.set_placeholder_text("Enter a duration")
		vbox.pack_start(self.time_entry, False, False, 0)

		hbox.pack_start(vbox, False, False, 0)

		output = Gtk.TextView()
		output.set_editable(False)
		output.set_size_request(300,100)
		self.output_buffer = output.get_buffer()
		hbox.pack_start(output, True, True, 0)

def main():
	token = get_token()
	win = TimerWindow(token, 'data/timer/track_cache.db')
	win.connect('destroy', Gtk.main_quit)
	win.show_all()
	Gtk.main()


if __name__ == '__main__':
	main()