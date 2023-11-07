# Example code for a job interview

def decode(message_file):
	lines = message_file.readlines()

	ordered_lines = {} # Dictionary used to store processed lines

	# Step 1: Work through the input data and populate the dictionary
	for line in lines:
		split_string = line.strip().split(" ", 1)
		index = int(split_string[0])
		body = split_string[1]

		ordered_lines[index] = body

	# Step 2: Determine which words will be in the output
	output = []
	
	next_index = 1
	increment = 2
	while next_index in ordered_lines:
		output.append(f"{next_index}: {ordered_lines[next_index]}")
		next_index += increment
		increment += 1

	# Step 3: Join the output list together and return to the user
	return "\n".join(output)



PATH = 'data/pyramid/input.txt'

if __name__ == '__main__':
	with open(PATH) as message:
		print(decode(message))