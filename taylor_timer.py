import requests
import base64
import json

# Fetch the app info from a hidden file
# Use this to generate an authorization token for the spotify api
client_info_loc = '/home/daniel/Development/tokens/SpotifyIDs.json'

with open(client_info_loc, 'r') as auth_file:
	auth_json = json.loads(auth_file.read())

	client_id = auth_json['client_id']
	client_secret = auth_json['client_secret']


url = 'https://accounts.spotify.com/api/token'
header_obj = { 
	'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode('ascii')).decode('ascii'),
	'Content-Type': 'application/x-www-form-urlencoded',
}

data_obj = 'grant_type=client_credentials'

response = requests.post(url, headers = header_obj, data = data_obj)

if response.status_code != 200:
	exit()

token = response.json()['access_token']
print(token)