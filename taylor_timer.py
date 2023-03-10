import requests
import base64
import json
import random
import bisect

# Fetch the app info from a hidden file
# Use this to generate an authorization token for the spotify api
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

# Get a list of all Taylor Swift albums
albums = []

offset = 0
while True:
	artists_album_url = 'https://api.spotify.com/v1/artists/06HL4z0CvFAxyc27GXpf02/albums?include_groups=album&market=US&limit=50&offset=' + str(offset)
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

# Iterate through all the albums and get a list of all Taylor Swift songs
sorted_tracks = []

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
				'id' : track['id'],
				'explicit' : track['explicit']
			}

			should_add = True
			for i, t in enumerate(sorted_tracks):
				if t['name'] == track_dict['name'] and (int(t['explicit']) >= int(track_dict['explicit'])):
					should_add = False
					break
				elif t['name'] == track_dict['name']:
					sorted_tracks[i] = track_dict
					should_add = False
					break

			if should_add:
				sorted_tracks.append(track_dict)



def track_len(t):
	return t['length']

sorted_tracks.sort(key=track_len)

# Determine which tracks can be combined to form a correct partition
print("Track DB Created")
print(len(sorted_tracks))

shuffled_tracks = sorted_tracks
random.shuffle(shuffled_tracks)

# 10 minutes in ms 
target_time = 100*60*1000

track_count = len(sorted_tracks)
med_len = (sorted_tracks[track_count // 2])['length']

tracks_needed = target_time // med_len
print("Looking for a combination of %d tracks" % (tracks_needed))

# Try every combination of n tracks in a pseudo random order
# Return early if a given combination has a total length within an acceptable threshold

# 10007 is prime. Assuming len(tracks) is less than 10007, then 10007^n is coprime to len(tracks)^n
# Therefore this will step through all the combinations of songs in pseudo-random order
increment = 10_007**tracks_needed
track_space = track_count**tracks_needed

test_index = 0

for i in range(10_000):
	test_tracks	= []
	working_val = test_index
	for t in range(tracks_needed):
		test_tracks.append(shuffled_tracks[working_val % track_count])
		working_val //= track_count

	test_len = 0
	for track in test_tracks:
		test_len += track['length']

	if abs(target_time - test_len) < 1000:
		print("Success!!!! Target time of %d, real time of %d" % (target_time, test_len))
		print("Completed in %d iterations" % (i))
		print()
		for t in test_tracks:
			print(t['name'])
		break

	test_index = (test_index + increment) % track_space