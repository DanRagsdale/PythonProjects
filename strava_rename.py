import os
import csv

FOLDER_LOCATION = 'data/strava_rename'
INPUT_FOLDER = 'activities'
INPUT_FILE = 'activities.csv'

ids_dict = {}

with open (FOLDER_LOCATION + '/' + INPUT_FILE, newline='\n') as csvfile :
	testReader = csv.reader(csvfile, delimiter=',')
	for row in testReader:
		file_loc = row[12]	
		filename = file_loc.replace("activities/","")
		file_id = filename.split('.')[0]

		name = row[2]

		ids_dict[file_id] = name

fail_count = 0
for i, filename in enumerate(os.listdir(FOLDER_LOCATION + '/' + INPUT_FOLDER)):
	split_name = filename.split('.')
	file_id = split_name[0]

	if file_id in ids_dict:
		split_name[0] = ids_dict[file_id].strip().replace('/', '-').replace(".","")
		new_name = '.'.join(split_name)
		#print(new_name, "  ", str(i))

		source = FOLDER_LOCATION + '/' + INPUT_FOLDER + '/' + filename
		dest = FOLDER_LOCATION + '/' + INPUT_FOLDER + '/' + new_name 

		if os.path.exists(dest):
			split_name[0] = ids_dict[file_id].strip().replace('/', '-') + str(i)
			new_name1 = '.'.join(split_name)
			dest = FOLDER_LOCATION + '/' + INPUT_FOLDER + '/' + new_name1
		try:
			os.rename(source, dest)
		except error:
			print(error)
	else:
		print(filename)
		fail_count += 1

print("Fail Count: ", fail_count)