import requests
import base64
import json
import random
import bisect
import typing
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from urllib.parse import quote
from pytimeparse.timeparse import timeparse

import sqlite3
import time

from bottle import Bottle, run, route, request
import webbrowser

class Track(typing.NamedTuple): 
	id: str
	name: str
	length: int
	uri: str
	explicit: bool

class Token(typing.NamedTuple):
	token: str
	has_user: bool

auth_token = None

# Fetch the app info from a hidden file
# Use this to generate an authorization token for the spotify api
# Token is not associated with a user so it is not possible to add songs to the queue
def request_token_no_user():
	global auth_token

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

	auth_token = Token(
		token = response.json()['access_token'],
		has_user = False
	)

# Requests an authorization token from the Spotify API
# Once the user accepts the authorization, a callback triggers the token generation process
def request_token():
	global auth_code

	client_info_loc = '/home/daniel/Development/tokens/SpotifyIDs.json'

	with open(client_info_loc, 'r') as auth_file:
		auth_json = json.loads(auth_file.read())
		client_id = auth_json['client_id']
		client_secret = auth_json['client_secret']

	webbrowser.open(f'https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri=http://localhost:8888/callback&scope=user-modify-playback-state')

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
		artists_album_url = f'https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album,single&market=US&limit=50&offset={offset}'
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

# Use the Spotify API to add the specified track to the user's play queue
def add_to_queue(token, track):
	queue_url = f'https://api.spotify.com/v1/me/player/queue?uri={track.uri}'
	header_obj = { 
		'Authorization': 'Authorization: Bearer ' + token,
		'Content-Type': 'application/json',
	}

	response = requests.post(queue_url, headers = header_obj)

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

# The server used to receive callbacks from the Spotify API
app = Bottle()

@app.route('/callback')
def auth_callback_listener():
	global auth_token
	
	client_info_loc = '/home/daniel/Development/tokens/SpotifyIDs.json'

	with open(client_info_loc, 'r') as auth_file:
		auth_json = json.loads(auth_file.read())
		client_id = auth_json['client_id']
		client_secret = auth_json['client_secret']

	print("Callback signled")

	auth_code = request.query['code']
	
	auth_url = 'https://accounts.spotify.com/api/token'
	header_obj = { 
		'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode('ascii')).decode('ascii'),
		'Content-Type': 'application/x-www-form-urlencoded',
	}
	data_obj = {
		'grant_type' : 'authorization_code',
		'code' : auth_code,
		'redirect_uri' : 'http://localhost:8888/callback'
	}

	response = requests.post(auth_url, headers = header_obj, data = data_obj)

	if response.status_code != 200:
		print(response)
		print(response.json())
		exit()

	auth_token = Token(
		token = response.json()['access_token'],
		has_user = True
	)

def run_server():
	run(app, host='127.0.0.1', port=8888)

class TimerWindow(Gtk.Window):
	def __init__(self, db_path):
		super().__init__(title="Hello World!")
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
		global auth_token

		if auth_token is None:
			print("Waiting to create authentication token.")
			return

		target_time = timeparse(self.time_entry.get_text())
		if target_time is None:
			print("Please enter a valid time!")
			return

		# Check if the tracks for the artist have been cached. If not, get them from the Spotify API
		artist_name = self.artist_entry.get_text().lower()
		cur_time = int(time.time())

		cached_artist = self.cursor.execute("SELECT artist_id, timestamp FROM artists WHERE artist_name = ?;", (artist_name,)).fetchone()
		if cached_artist is None or (cur_time - cached_artist[1] > 3600):
			print("Getting new Data!!")
			print(cached_artist)
		
			artist_id = get_artist_id(auth_token.token, artist_name)
			self.cursor.execute("INSERT OR REPLACE INTO artists VALUES(?, ?, ?);", (artist_id, artist_name, cur_time,))		
			
			albums = get_albums(auth_token.token, artist_id)
			tracks = get_tracks(auth_token.token, albums)

			track_data = [(t.id, artist_id, t.name, t.length, t.uri) for t in tracks]
			self.cursor.executemany("INSERT OR REPLACE INTO tracks VALUES(?, ?, ?, ?, ?);", track_data)
			self.db_connection.commit()
		else:
			print("Valid cache found!")
			raw_tracks = self.cursor.execute("SELECT track_id, track_name, track_len, track_uri FROM tracks WHERE artist_id = ?;", (cached_artist[0],)).fetchall()
			tracks = [Track(id=t[0], name=t[1], length=t[2], uri=t[3], explicit=True) for t in raw_tracks]

		track_list = find_playlist(tracks, target_time*1000)

		# Display the playlist in the app window
		disp_string = '\n'.join(track.name for track in track_list)
		self.output_buffer.set_text(disp_string)

		# Add the playlist to the user's Spotify Queue
		if auth_token.has_user:
			for track in track_list:
				add_to_queue(auth_token.token, track)

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
	server_thread = threading.Thread(target=run_server, name='server')
	server_thread.daemon = True
	server_thread.start()

	request_token()
	win = TimerWindow('data/timer/track_cache.db')
	win.connect('destroy', Gtk.main_quit)
	win.show_all()
	Gtk.main()


if __name__ == '__main__':
	main()