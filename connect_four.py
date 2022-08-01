import pygame
import sys, os

from pygame.locals import (
	K_1,
	K_2,
	K_3,
	K_4,
	K_5,
	K_6,
	K_7,
	
	K_SPACE,
	K_ESCAPE,
	KEYDOWN,
	QUIT
	)

IMAGE_SOURCES = [
	"piece_red.png",
	"piece_yellow.png"
]

IMAGES = []

pygame.init()

pygame.display.set_caption("Connect 4")
window = pygame.display.set_mode((800,600))

font = pygame.font.SysFont("Arial Black", 30)

module = sys.modules['__main__']
path, name = os.path.split(module.__file__)

for tag in IMAGE_SOURCES:
	print(os.path.join(path, "res", "connect", tag))
	img = pygame.image.load(os.path.join(path, "res", "connect", tag))
	img.convert()

	IMAGES.append(img)


background = pygame.Surface((800,600))
background.fill((0,0,0))

surf_board = pygame.Surface((700,600))
surf_board.fill((128,128,128))


current_turn = board = None

def reset_game():
	global board, state, current_turn
	board = [[-1 for y in range(6)] for x in range(7)] 
	current_turn = 0

def drop_piece(column, type):
	for i in range(5,-1,-1):
		if board[column][i] == -1:
			board[column][i] = type
			return True
	return False

def check_board():
	#Vertical
	for x in range(0,7):
		for y in range(0,3):
			if board[x][y] == board[x][y+1] == board[x][y+2] == board[x][y+3] != -1:
				return True
	#Horizontal
	for x in range(0,4):
		for y in range(0,6):
			if board[x][y] == board[x+1][y] == board[x+2][y] == board[x+3][y] != -1:
				return True
	#Diagonal Down
	for x in range(0,4):
		for y in range(0,3):
			if board[x][y] == board[x+1][y+1] == board[x+2][y+2] == board[x+3][y+3] != -1:
				return True
	#Diagonal Up
	for x in range(0,4):
		for y in range(3,6):
			if board[x][y] == board[x+1][y-1] == board[x+2][y-2] == board[x+3][y-3] != -1:
				return True

	return False



reset_game()

# State 0, -1, -2 is Menu
# State 1 is Singleplayer
# State 2 is Multiplayer
state = 0
running = True
while running:
	events = pygame.event.get()

	for event in events:
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				running = False
		if event.type == QUIT:
			running = False


	if state == 0:
		for event in events:
			if event.type == KEYDOWN:
				if event.key == K_SPACE:
					state = 2
					reset_game()
	elif state == 1:
		pass
	elif state == 2:
		for event in events:	
			if event.type == KEYDOWN:	
				if event.key in range(K_1,K_7+1) and drop_piece(event.key - K_1, current_turn):
					current_turn = (current_turn + 1) % 2

					if check_board():
						print("Game Over!!")
						state = 0


	# Render Code
	background.fill((0,0,0))
	surf_board.fill((128,128,128))
	for x in range(0,7):
		for y in range(0,6):
			if board[x][y] == -1 and y == 0:
				column_num = font.render(str(x + 1), True, (0,0,0))
				text_coord = column_num.get_rect(center=(x*100 + 50, y*100 + 50))
				pygame.Surface.blit(surf_board, column_num, text_coord)
			elif board[x][y] != -1:
				coord = pygame.Rect(x * 100, y * 100, 100, 100)
				pygame.Surface.blit(surf_board,IMAGES[board[x][y]], coord)

	if state == 0:
		pass
	else:
		pygame.Surface.blit(background,IMAGES[current_turn], (7*100, 0))


	pygame.Surface.blit(window,background, (0,0))
	pygame.Surface.blit(window,surf_board, (0,0))

	pygame.display.update()