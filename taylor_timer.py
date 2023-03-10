import requests
import base64
import json
import random
import bisect

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

# Iterate through all the albums and get a list of all Taylor Swift songs
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
				track_dict = {
					'name' : track['name'],
					'length' : track['duration_ms'],
					'explicit' : track['explicit'],
					'id' : track['id'],
					'uri' : track['uri'],
				}

				should_add = True
				for i, t in enumerate(tracks):
					if t['name'] == track_dict['name'] and (int(t['explicit']) >= int(track_dict['explicit'])):
						should_add = False
						break
					elif t['name'] == track_dict['name']:
						tracks[i] = track_dict
						should_add = False
						break

				if should_add:
					tracks.append(track_dict)
	return tracks


def track_len(t):
	return t['length']

# Determine which tracks can be combined to form a correct partition
def generate_playlist(tracks, target_time):
	tracks.sort(key=track_len)

	track_count = len(tracks)
	med_len = (tracks[track_count // 2])['length']

	tracks_needed = target_time // med_len
	print(f"Looking for a combination of {tracks_needed} tracks")

	random.shuffle(tracks)

	# Try every combination of n tracks in a pseudo random order
	# Return early if a given combination has a total length within an acceptable threshold

	# 10007 is prime. Assuming len(tracks) is less than 10007, then 10007^n is coprime to len(tracks)^n
	# Therefore this will step through all the combinations of songs in pseudo-random order
	increment = 10_007**tracks_needed
	track_space = track_count**tracks_needed

	test_index = 0

	for i in range(100_000):
		test_tracks	= []
		working_val = test_index
		for t in range(tracks_needed):
			test_tracks.append(tracks[working_val % track_count])
			working_val //= track_count

		test_len = sum([track['length'] for track in test_tracks])

		if abs(target_time - test_len) < 1000:
			print(f"Success!!!! Target time of {target_time}, real time of {test_len}")
			print(f"Completed in {i} iterations")
			print()
			return test_tracks
		
		test_index = (test_index + increment) % track_space

	print("Failed :(")


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from urllib.parse import quote
from pytimeparse.timeparse import timeparse

class TimerWindow(Gtk.Window):
	def __init__(self, token):
		super().__init__(title="Hello World!")

		self.token = token

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

	def generate_playlist(self, widget):

		target_time = timeparse(self.time_entry.get_text())
		if target_time is None:
			print("Please enter a valid time!")
			return
		
		artist_id = get_artist_id(self.token, self.artist_entry.get_text())
		albums = get_albums(self.token, artist_id)
		tracks = get_tracks(self.token, albums)
		
		print("Track DB Created")

		track_list = generate_playlist(tracks, target_time*1000)

		disp_string = '\n'.join(track['name'] for track in track_list)
		self.output_buffer.set_text(disp_string)

def main():
	token = get_token()
	win = TimerWindow(token)
	win.connect('destroy', Gtk.main_quit)
	win.show_all()
	Gtk.main()



if __name__ == '__main__':
	main()