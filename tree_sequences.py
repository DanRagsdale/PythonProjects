import random

COLORS = ['A','B','C']
VALID_COLORS = ['B','C']


class Tree:
	def __init__(self):
		self.color = 'C'
		self.children = []
	
	def get_length(self):
		if self.children == []:
			return 1
		
		counter = 1
		for child in self.children:
			counter += child.get_length()

		return counter

def is_embeddable(small, large):
	# does small have the same root as large?

	# does root of small one of the children of large? etc.

	return True


def generate_subtree(max_len, b_limit):
		remaining_len = max_len - 1

		t = Tree()

		if b_limit > 1:
			b_limit -= 1
		elif b_limit == 1:
			t.color = random.choice(VALID_COLORS)

		if t.color == "B":
			if remaining_len >= 2:
				c_0 = Tree()
				c_0.color = "C"
				c_1 = Tree()
				c_1.color = "C"

				c_0.children.append(c_1)
				t.children.append(c_0)
			elif remaining_len >= 1:
				c_0 = Tree()
				c_0.color = "C"

				t.children.append(c_0)
		else:
			while remaining_len > 0:
				next_len = random.randint(1, remaining_len)
				child_tree = generate_subtree(next_len, b_limit)
				
				t.children.append(child_tree)
				remaining_len -= child_tree.get_length()

		return t


# Randomly generate a tree that meets certain criteria:
# Tree will not contain any nodes with A coloring
# Tree will not embed b--b
# Tree will not embed c--B--c
# Tree will not embed B--c--c--c
def generate_tree(length):
	remaining_length = length
	b_limit = 1
	
	remaining_length -= 1

	while remaining_length > 0:
		sub_tree = generate_subtree(1,1)
		remaining_length -=1
	
	return Tree()




def visualize(tree, depth):
	if depth == 0:
		print(tree.color)
	else:
		print (' ' * (depth - 1) + '└' + tree.color)

	for child in tree.children:
		visualize(child, depth + 1)


n = 7
t = generate_subtree(8, 2)

visualize(t, 0)

print()
#print(is_embeddable(a, t))