import pygame
import sys, os
import random

from pathlib import Path

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
GAMEOVER = pygame.USEREVENT + 2

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

pygame.init()
pygame.font.init()

window = pygame.display.set_mode([SCREEN_WIDTH + 300, SCREEN_HEIGHT + 100])
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
gui = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Simple Tetris")

font = pygame.font.SysFont("Arial Black", 30)

pygame.key.set_repeat(160, 50)

module = sys.modules['__main__']
path, name = os.path.split(module.__file__)

for tag in IMAGE_SOURCES:
	print(os.path.join(path, "res", "tetris", tag))
	img = pygame.image.load(os.path.join(path, "res", "tetris", tag))
	img.convert()

	IMAGES.append(img)


clear_multiplier = [0, 40, 100, 300, 1200]
high_score = 0


FOLDER_LOCATION = 'data/simple_tetris'
FILE_NAME = 'high_score.txt'

Path(FOLDER_LOCATION).mkdir(parents=True, exist_ok=True)
with open (FOLDER_LOCATION + '/' + FILE_NAME, 'a+', newline='\n') as f:
	f.seek(0)
	line = f.readline()
	if line.isdigit():
		high_score = int(line)
	

# Begin game logic
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
			if self.y == 0:
				pygame.event.post(pygame.event.Event(GAMEOVER))
			else:
				pygame.event.post(pygame.event.Event(FIXPIECE))
			return False

	def draw(self, screen):
		origin_x = self.x * BLOCK_SIZE
		origin_y = self.y * BLOCK_SIZE

		for point in self.points:
			rect = (origin_x + point[0] * BLOCK_SIZE, origin_y + point[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
			pygame.Surface.blit(screen,IMAGES[self.block_type], rect)

board = piece = next_piece = clock = current_frame = last_frame = last_fix = drop_frames = lines_cleared = score = None

def reset_board():
	global board, piece, next_piece, clock, current_frame, last_frame, last_fix, drop_frames, lines_cleared, score
	board = [[0 for y in range(20)] for x in range(10)] 

	piece = Piece()
	next_piece = Piece()
	clock = pygame.time.Clock()

	current_frame = 0
	last_frame = 0
	last_fix = 0
	drop_frames = 70

	lines_cleared = 0
	score = 0


# Begin game loop

reset_board()

running = True
alive = True
while running:
	# Event Handler
	events = pygame.event.get()
	for event in events:
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				running = False

		elif event.type == QUIT:
			running = False


	if alive:
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
			elif event.type == GAMEOVER:
				alive = False

			elif event.type == FIXPIECE and current_frame !=  last_fix:
				# add the current piece to the board, clear completed lines and create a new piece	
				for point in piece.points:
					board[piece.x + point[0]][piece.y + point[1]] = piece.block_type
				
				initial_lines = lines_cleared

				y = 19
				while y > 0:
					flag = True
					for x in range(10):
						if board[x][y] == 0:
							flag = False
					if flag:
						lines_cleared += 1
						for y1 in range(y, 0, -1):
							for x in range(10):
								board[x][y1] = board[x][y1 - 1]

						if lines_cleared % 10 == 0:
							if(drop_frames > 30):
								drop_frames = int(drop_frames * 0.9)
							else:
								drop_frames = int(drop_frames * 0.95)
							print("Drop frames: ", drop_frames)
					else:
						y -= 1

				score += clear_multiplier[lines_cleared - initial_lines] * (lines_cleared // 10 + 1)
				if score > high_score:
					high_score = score
				
				piece = next_piece
				next_piece = Piece()
				last_fix = current_frame

		if current_frame - last_frame > drop_frames:
			piece.drop()
			last_frame = current_frame
	else:
		for event in events:
			if event.type == KEYDOWN:
				if event.key == K_SPACE:
					reset_board()
					alive = True

	current_frame += 1

	# Render Code
	if alive:
		screen.fill((0,0,0))
		piece.draw(screen)

		for x in range(10):
			for y in range(20):
				if board[x][y] != 0:
					origin_x = x * BLOCK_SIZE
					origin_y = y * BLOCK_SIZE

					rect = (origin_x, origin_y, BLOCK_SIZE, BLOCK_SIZE)
					pygame.Surface.blit(screen,IMAGES[board[x][y]], rect)

		gui.fill((128,128,128))
		next_piece.draw(gui)

		score_text = font.render('Score: ' + str(score), False, (0,0,0))
		lines_text = font.render('Lines: ' + str(lines_cleared), False, (0,0,0))

		if score == high_score:
			hs_text = font.render('Best: ' + str(high_score), True, (255,0,0),(0,0,0))
		else:
			hs_text = font.render('Best: ' + str(high_score), False, (0,0,0))

		pygame.Surface.blit(gui,score_text, (2.5 * BLOCK_SIZE, 5 * BLOCK_SIZE))
		pygame.Surface.blit(gui,lines_text, (2.5 * BLOCK_SIZE, 6 * BLOCK_SIZE))
		pygame.Surface.blit(gui,hs_text, (2.5 * BLOCK_SIZE, 9 * BLOCK_SIZE))
	else:
		gameover_text0 = font.render('Game Over', True, (255,255,255),(0,0,0))
		gameover_text1 = font.render('Press SPACE to reset', True, (255,255,255),(0,0,0))
		pygame.Surface.blit(screen, gameover_text0, (2.5 * BLOCK_SIZE, 4 * BLOCK_SIZE))
		pygame.Surface.blit(screen, gameover_text1, (0.5 * BLOCK_SIZE, 5 * BLOCK_SIZE))

		
	window.fill((128,128,128))
		
	pygame.Surface.blit(window, gui, (350, 100))
	pygame.Surface.blit(window, screen, (50,50))

	pygame.display.flip()
	clock.tick(120)

# Save high score

Path(FOLDER_LOCATION).mkdir(parents=True, exist_ok=True)
with open (FOLDER_LOCATION + '/' + FILE_NAME, 'w+', newline='\n') as f:
	f.write(str(high_score))

pygame.quit()

















