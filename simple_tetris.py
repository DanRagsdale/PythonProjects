import pygame
import sys, os
import random

from pygame.locals import (
	K_UP,
	K_DOWN,
	K_LEFT,
	K_RIGHT,
	K_z,
	K_SPACE,
	K_ESCAPE,
	KEYDOWN,
	QUIT
)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 800 

BLOCK_SIZE = SCREEN_WIDTH / 10

FIXPIECE = pygame.USEREVENT + 1

board = [[0 for y in range(20)] for x in range(10)] 

PIECES = [
  [(0,0),(0,0),(0,0),(0,0)],
	[(0,0),(1,0),(2,0),(1,1)],
	[(0,0),(0,1),(1,0),(1,1)], 
	[(0,0),(1,0),(2,0),(0,1)],
	[(0,0),(1,0),(2,0),(2,1)],
	[(1,0),(2,0),(0,1),(1,1)],
	[(0,0),(1,0),(1,1),(2,1)],
	[(0,0),(1,0),(2,0),(3,0)]
]

COLORS = [
	(255,255,255),
	(255,255,255),
	(255,255,255),
	(255,255,255),
	(255,255,255),
	(255,255,255),
	(255,255,255),
	(255,255,255),
]

IMAGE_SOURCES = [
	"block_blue.png",
	"block_cyan.png",
	"block_orange.png",
	"block_purple.png",
	"block_red.png",
	"block_turquoise.png",
	"block_yellow.png",
]

IMAGES = [None]

class Piece(pygame.sprite.Sprite):
	def __init__(self):
		super(Piece, self).__init__()
		self.block_type = random.randint(1,7)

		self.x, self.y = (4,0)
		self.points = PIECES[self.block_type]

	def shiftl(self):
			can_shift = True
			for point in self.points:
				if self.x <= 0 or board[self.x + point[0] - 1][self.y + point[1]] != 0:
					can_shift = False
			if can_shift:
				self.x -= 1
	def shiftr(self):
			can_shift = True
			for point in self.points:
				if self.x + point[0] >= 9 or board[self.x + point[0] + 1][self.y + point[1]] != 0:
					can_shift = False
			if can_shift:
				self.x += 1
	def spinr(self):
		min_x, max_y = 0, 0
		for point in self.points:
			if point[0] < min_x:
				min_x = point[0]
			if point[1] > max_y:
				max_y = point[1]

		test_points = [0,0,0,0]
		for i in range(4):
			test_points[i] = (-self.points[i][1] + max_y, self.points[i][0] - min_x)

		can_spin = True
		for tp in test_points:
			if self.x + tp[0] < 0 or self.x + tp[0] > 9 or self.y + tp[1] > 19 or board[self.x + tp[0]][self.y + tp[1]] != 0:
				can_spin = False

		if can_spin:
			self.points = test_points
	def spinl(self):
		max_x, min_y = 0, 0
		for point in self.points:
			if point[0] > max_x:
				max_x = point[0]
			if point[1] < min_y:
				min_y = point[1]

		test_points = [0,0,0,0]
		for i in range(4):
			test_points[i] = (self.points[i][1] - min_y, -self.points[i][0] + max_x)

		can_spin = True
		for tp in test_points:
			if self.x + tp[0] < 0 or self.x + tp[0] > 9 or self.y + tp[1] > 19 or board[self.x + tp[0]][self.y + tp[1]] != 0:
				can_spin = False

		if can_spin:
			self.points = test_points

	def drop(self):
		can_drop = True
		for point in self.points:
			if self.y + point[1] >= 19 or board[self.x + point[0]][self.y + point[1] + 1] != 0:
				can_drop = False

		if can_drop:
			self.y += 1
		else:
			pygame.event.post(pygame.event.Event(FIXPIECE))
			return False

	def draw(self, screen):
		origin_x = self.x * BLOCK_SIZE
		origin_y = self.y * BLOCK_SIZE

		for point in self.points:
			rect = (origin_x + point[0] * BLOCK_SIZE, origin_y + point[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
			pygame.Surface.blit(screen,IMAGES[self.block_type], rect)

window = pygame.display.set_mode([SCREEN_WIDTH + 300, SCREEN_HEIGHT + 100])
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
gui = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.init()

pygame.key.set_repeat(160, 50)

module = sys.modules['__main__']
path, name = os.path.split(module.__file__)

for tag in IMAGE_SOURCES:
	print(os.path.join(path, "res", "tetris", tag))
	img = pygame.image.load(os.path.join(path, "res", "tetris", tag))
	img.convert()

	IMAGES.append(img)

# Begin game code
piece = Piece()
next_piece = Piece()
clock = pygame.time.Clock()

current_frame = 0
last_frame = 0
last_fix = 0
drop_frames = 70

lines_cleared = 0

running = True
alive = True
while alive:
	# Event Handler
	events = pygame.event.get()
	for event in events:
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				running = False
				alive = False

		elif event.type == QUIT:
			running = False
			alive = False


	if running:
		pressed_keys = pygame.key.get_pressed()
		for event in events:
			if event.type == KEYDOWN:
				if event.key == K_LEFT and not pressed_keys[K_RIGHT]:
					piece.shiftl()
				elif event.key == K_RIGHT and not pressed_keys[K_LEFT]:
					piece.shiftr()
				elif event.key == K_DOWN:
					piece.drop()
				elif event.key == K_UP and not pressed_keys[K_z]:
					piece.spinr()
				elif event.key == K_z and not pressed_keys[K_UP]:
					piece.spinl()
				elif event.key == K_SPACE and current_frame - last_fix > 30:
					while piece.drop() != False:
						pass
			elif event.type == FIXPIECE and current_frame !=  last_fix:
				# add the current piece to the board, clear completed lines and create a new piece	
				for point in piece.points:
					board[piece.x + point[0]][piece.y + point[1]] = piece.block_type

				y = 19
				while y > 0:
					flag = True
					for x in range(10):
						if board[x][y] == 0:
							flag = False
					if flag:
						lines_cleared += 1
						if lines_cleared % 10 == 0:
							if(drop_frames > 30):
								drop_frames = int(drop_frames * 0.9)
							else:
								drop_frames = int(drop_frames * 0.95)
							print("Drop frames: ", drop_frames)

						print(str(lines_cleared) + " lines cleared")
						for y1 in range(y, 0, -1):
							for x in range(10):
								board[x][y1] = board[x][y1 - 1]
					else:
						y -= 1
				piece = next_piece
				next_piece = Piece()
				last_fix = current_frame

		if current_frame - last_frame > drop_frames:
			piece.drop()
			last_frame = current_frame

		# Game Code
		screen.fill((0,0,0))
		piece.draw(screen)

		for x in range(10):
			for y in range(20):
				if board[x][y] != 0:
					origin_x = x * BLOCK_SIZE
					origin_y = y * BLOCK_SIZE

					rect = (origin_x, origin_y, BLOCK_SIZE, BLOCK_SIZE)
					pygame.Surface.blit(screen,IMAGES[board[x][y]], rect)

		current_frame += 1
		
		window.fill((128,128,128))
		
		gui.fill((128,128,128))
		next_piece.draw(gui)
		pygame.Surface.blit(window, gui, (350, 100))
		pygame.Surface.blit(window, screen, (50,50))

	pygame.display.flip()
	clock.tick(120)

pygame.quit()















