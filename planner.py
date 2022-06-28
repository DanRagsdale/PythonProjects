import os
import csv
import atexit
import shlex

from pathlib import Path

STATUS = 'Status'
NAME = 'Name'
DESCRIPTION = 'Description'

FOLDER_LOCATION = 'data/planner'
FILE_NAME = 'test.csv'

plannerList = []

def save_list():
	Path(FOLDER_LOCATION).mkdir(parents=True, exist_ok=True)
	with open (FOLDER_LOCATION + '/' + FILE_NAME, 'w+', newline='\n') as csvfile :
		fieldnames = [STATUS, NAME, DESCRIPTION]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		
		writer.writeheader()
		for row in plannerList:
			writer.writerow(row)

def print_list():
	os.system('cls||clear')
	print("   "+STATUS+" "+NAME+"       "+DESCRIPTION)
	
	index = 0
	for row in plannerList:
		iP = 3 - len(str(index))
		sP = 6 - len(row[STATUS])
		nP = 10 - len(row[NAME])


		print(str(index) + iP*' ' + row[STATUS] + sP * ' ', row[NAME] + nP * ' ', row[DESCRIPTION])
		index += 1

def exit_handler():
	print("Saving List...")
	save_list()


atexit.register(exit_handler)


Path(FOLDER_LOCATION).mkdir(parents=True, exist_ok=True)
with open (FOLDER_LOCATION + '/' + FILE_NAME, 'a+', newline='\n') as csvfile :
	csvfile.seek(0)
	testReader = csv.DictReader(csvfile)
	print(testReader)
	for row in testReader:
		plannerList.append(row)

while True:
	print_list()
	print()
	x = input("Please enter a command\n")
	com = shlex.split(x)

	if len(com) > 0 and com[0].lower() == 'x':
		exit()

	if len(com) == 2 and com[0].lower() == 'add':
		plannerList.append({STATUS:"FALSE", NAME:com[1], DESCRIPTION:""})
	if len(com) > 2 and com[0].lower() == 'add':
		plannerList.append({STATUS:"FALSE", NAME:com[1], DESCRIPTION:com[2]})

	if len(com) == 2 and com[0].lower() == 'del':
		if com[1].isdigit():
			plannerList.pop(int(com[1]))
		else:
			plannerList = [x for x in plannerList if not x[NAME] == com[1]]
			

	if len(com) == 2 and com[0].lower() == 'toggle':
		if com[1].isdigit():
			index = int(com[1])
			if plannerList[index][STATUS] == "TRUE":
				plannerList[index][STATUS] = "FALSE"
			else:
				plannerList[index][STATUS] = "TRUE"
		else:
			for row in plannerList:
				if row[NAME] == com[1]:
					if row[STATUS] == "TRUE":
						row[STATUS] = "FALSE"
					else:
						row[STATUS] = "TRUE"
