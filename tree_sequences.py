from cProfile import run
import random
import itertools

from manim import *

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

	def get_vertices(self):
		verts = [self]
		for child in self.children:
			verts.extend(child.get_vertices())
		return verts

	def get_edges(self):
		edges = []
		for child in self.children:
			edges.append((self,child))
			edges.extend(child.get_edges())
		return edges



def is_embeddable(small, large):
	# Are the roots the same color, is small total length less, and do we have fewer children than large?
	# If *yes* check if our children can be embedded in the children of large. Will have to check all permutations
	# 	If *yes*, then we are good
	#	If *no*, then check if small can be embedded as one of the children of large

	# If *no* check if small can be embedded as one of the children of large

	if small.get_length() > large.get_length():
		return False
	if len(small.children) > len(large.children):
		return False

	flag = False

	if small.color == large.color:
		flag = True
		if len(small.children) > 0:
			for order in itertools.permutations(range(0, len(large.children)), len(small.children)):
				flag = True
				for i in range(0, len(small.children)):
					flag *= is_embeddable(small.children[i], large.children[order[i]])
				if flag:
					break

	# Check if small can be embedded as a child of large
	if not flag:
		for child in large.children:
			flag = flag or is_embeddable(small, child)


	return bool(flag)


# Randomly generate a tree that meets certain criteria:
# Tree will not contain any nodes with A coloring
# Tree will not embed B--b
# Tree will not embed c--B--c
# Tree will not embed B--c--c--c
def generate_tree(max_len, b_limit):
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
				child_tree = generate_tree(next_len, b_limit)
				
				t.children.append(child_tree)
				remaining_len -= child_tree.get_length()

		return t



def visualize(tree, depth):
	if depth == 0:
		print(tree.color)
	else:
		print (' ' * (depth - 1) + '└' + tree.color)

	for child in tree.children:
		visualize(child, depth + 1)


class Count(Animation):
	def __init__(self, number: DecimalNumber, start: float, end: float, **kwargs) -> None:
		super().__init__(number, **kwargs)
		self.start = start
		self.end = end

	def interpolate_mobject(self, alpha: float) -> None:
		value = self.start + alpha * (self.end - self.start)
		self.mobject.set_value(value)

class Vertex:
	def __init__(self, index, color):
		self.index = index
		self.color = color

class TestManim(Scene):
	def construct(self):
		
		t = generate_tree(10, 2)
		visualize(t,0)

		t_verts = t.get_vertices()
		t_edges = t.get_edges()

		red_verts = {}
		for v in t_verts:
			if v.color == "A":
				red_verts[v] = {"fill_color":BLUE}
			elif v.color == "B":
				red_verts[v] = {"fill_color":RED}
			elif v.color == "C":
				red_verts[v] = {"fill_color":GREEN}

		g = Graph(t_verts, t_edges, 
			layout="tree", 
			vertex_config=red_verts,
			root_vertex=t_verts[0])

		self.play(Create(g))
		self.wait()
		
		#num = DecimalNumber().set_color(WHITE).scale(5)
		#self.add(num)
		#self.play(Count(num, 10, 100), run_time=4.0)