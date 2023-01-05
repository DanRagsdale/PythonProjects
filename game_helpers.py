import pygame
from pygame.locals import *

from PIL import Image

# This class handles sprite sheets
# This was taken from www.scriptefun.com/transcript-2-using
# sprite-sheets-and-drawing-the-background
class Spritesheet(object):
	def __init__(self, filename, size_x, size_y):
		self.sheet = pygame.image.load(filename).convert()
		self.size_x = size_x
		self.size_y = size_y
    
	def image_from_index(self, x, y, colorkey=None):
		return self.image_at((x * self.size_x, y * self.size_y, self.size_x, self.size_y), colorkey)
	
	# Load a specific image from a specific rectangle
	def image_at(self, rectangle, colorkey = None):
		"Loads image from x,y,x+offset,y+offset"
		rect = pygame.Rect(rectangle)
		image = pygame.Surface(rect.size).convert()
		image.blit(self.sheet, (0, 0), rect)
		if colorkey is not None:
			if colorkey is -1:
				colorkey = image.get_at((0,0))
			image.set_colorkey(colorkey, pygame.RLEACCEL)
		return image

    # Load a whole bunch of images and return them as a list
	def images_at(self, rects, colorkey = None):
		"Loads multiple images, supply a list of coordinates" 
		return [self.image_at(rect, colorkey) for rect in rects]
	# Load a whole strip of images
	def load_strip(self, y, image_count, colorkey = None):
		"Loads a strip of images and returns them as a list"
		tups = [(x * self.size_x, y * self.size_y, self.size_x, self.size_y) for x in range(image_count)]
		return self.images_at(tups, colorkey)


# Returns the intersection point (x, y)
# Returns () if the lines do not intersect
# Lines are inputed in 2-point form
# ray = (x1, y1, x2-x1, y2-y1)
# line = (x3, y3, x4, y4)
def check_ray_line_collision(ray, line):
	x1, y1 = ray[0:2]
	x2 = x1 + ray[2]
	y2 = y1 + ray[3]

	x3, y3, x4, y4 = line

	Denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
	if Denom == 0:
		return ()

	Nt = (x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)
	t = Nt / Denom
	if t < 0:
		return ()

	Nx = (x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)
	Ny = (x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)

	return (Nx/ Denom, Ny / Denom)

def distance(a,b):
	return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def check_point_on_segment(point, segment):
	return -0.01 < distance(point,segment[0:2]) + distance(point,segment[2:4]) - distance(segment[0:2],segment[2:4]) < 0.01

# Ray has the form (x, y, x_magnitue, y_magnitude)
# Rect is a pygame Rect
# Return distance between ray start point and a rectange.
# Return infinty if there is no collision
def check_ray_rect_collision_point(ray, rect):
	collisions = []

	#line_ray = (ray[0], ray[1], ray[0]+ray[2], ray[1]+ray[3])
	if ray[0] < rect.left:
		line_left = rect.topleft + rect.bottomleft
		col_l = check_ray_line_collision(ray, line_left)
		if col_l and check_point_on_segment(col_l, line_left):
			collisions.append(col_l)

	if ray[0] > rect.right:
		line_right = rect.topright + rect.bottomright
		col_r = check_ray_line_collision(ray, line_right)
		if col_r and check_point_on_segment(col_r, line_right):
			collisions.append(col_r)

	if ray[1] < rect.top:
		line_top = rect.topleft + rect.topright
		col_t = check_ray_line_collision(ray, line_top)
		if col_t and check_point_on_segment(col_t, line_top):
			collisions.append(col_t)

	if ray[1] > rect.bottom:
		line_bottom = rect.bottomleft + rect.bottomright
		col_b = check_ray_line_collision(ray, line_bottom)
		if col_b and check_point_on_segment(col_b, line_bottom):
			collisions.append(col_b)

	if collisions:
		dists = [distance(ray[0:2], p) for p in collisions]
		min_dist = min(dists)
		return min_dist, collisions[dists.index(min_dist)]
	else:
		return float('inf'), ()

def check_ray_rect_collision(ray, rect):
	return check_ray_rect_collision_point(ray, rect)[0]

