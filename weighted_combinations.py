import numpy as np

team_members = [
		("A", 1),
		("B", 1),
		("C", 2),
		("D", 2),
		("E", 3),
		("F", 3),
		("G", 1),
		("H", 1),
		("I", 1),
		("J", 1)
	]

output_len = 10


# Code

total_weight = 0

for s in team_members:
	total_weight += s[1]

skater_names = []
skater_probabilities = []

for s in team_members:
	skater_names.append(s[0])
	skater_probabilities.append(s[1]/ total_weight)

for i in range(output_len):
	lineup = np.random.choice(
		skater_names,
		size=4,
		p=skater_probabilities
	)

	print("%s, %s, %s, %s," % tuple(lineup))