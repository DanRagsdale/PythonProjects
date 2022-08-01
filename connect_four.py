import pygame
import random
import sys, os
import copy

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
	"piece_yellow.png",
	"grid.png"
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
	board = [[0 for y in range(6)] for x in range(7)] 
	current_turn = 1

def drop_piece(test_board, column, type):
	for i in range(5,-1,-1):
		if test_board[column][i] == 0:
			test_board[column][i] = type
			return True
	return False

def check_board(test_board):
	#Vertical
	for x in range(0,7):
		for y in range(0,3):
			if test_board[x][y] == test_board[x][y+1] == test_board[x][y+2] == test_board[x][y+3] != 0:
				return test_board[x][y]
	#Horizontal
	for x in range(0,4):
		for y in range(0,6):
			if test_board[x][y] == test_board[x+1][y] == test_board[x+2][y] == test_board[x+3][y] != 0:
				return test_board[x][y]
	#Diagonal Down
	for x in range(0,4):
		for y in range(0,3):
			if test_board[x][y] == test_board[x+1][y+1] == test_board[x+2][y+2] == test_board[x+3][y+3] != 0:
				return test_board[x][y]
	#Diagonal Up
	for x in range(0,4):
		for y in range(3,6):
			if test_board[x][y] == test_board[x+1][y-1] == test_board[x+2][y-2] == test_board[x+3][y-3] != 0:
				return test_board[x][y]

	#Check draw
	for x in range(0,7):
		if test_board[x][0] == 0:
			return 0
	return 2

def eval_position(test_board):
	return 1000 * check_board(test_board)

def eval_board(test_board, test_turn, depth):
	# if the board has 4 in a row, return +/- 1000
	check_result = check_board(test_board)
	if check_result:
		return check_result * 1000
	
	if depth == 0:
		return eval_position(test_board)

	# otherwise check possible options until depth is reached
	evals = []

	for i in range(0,7):
		copy_board = copy.deepcopy(test_board)
		drop_piece(copy_board, i, test_turn)
		evals.append(test_turn * eval_board(copy_board, test_turn * -1, depth - 1))
	
	eval = test_turn * max(evals)

	#Prioritize avoiding quick losses/ going for quick wins if there are multiple forced wins
	if abs(eval) > 500:
		return 0.95 * eval
	else:
		return eval

def generate_move(test_board, test_turn):
	#for i in range(0,7):
	#	copy_board = copy.deepcopy(board)
	#	drop_piece(copy_board, i, test_turn)
	#	if eval_board(copy_board, test_turn, 5) < 0:
	#		return i
	evals = []
	for i in range(0,7):
		copy_board = copy.deepcopy(test_board)
		drop_piece(copy_board, i, test_turn)
		evals.append(eval_board(copy_board, test_turn * -1, 5))

	target = 1000
	index = -1

	print(evals)
	shuffled_range = random.sample(range(0,7), 7)
	for i in shuffled_range:
		if evals[i] < target and test_board[i][0] == 0:
			target = evals[i]
			index = i
	
	return index
		


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
					state = 1
					reset_game()
	elif state == 1:
		if current_turn == 1:
			#print(eval_board(board,current_turn,4))
			for event in events:
				if event.type == KEYDOWN:	
					if event.key in range(K_1,K_7+1) and drop_piece(board, event.key - K_1, current_turn):
						current_turn *= -1

						if check_board(board):
							print("Game Over!!")
							state = 0
		else:
			move = generate_move(board, current_turn)
			drop_piece(board, move, current_turn)
			current_turn *= -1
				
			if check_board(board):
				print("Game Over!!")
				state = 0

	elif state == 2:
		print(eval_board(board,current_turn,6))
		for event in events:	
			if event.type == KEYDOWN:	
				if event.key in range(K_1,K_7+1) and drop_piece(board, event.key - K_1, current_turn):
					current_turn *= -1

					if check_board(board):
						print("Game Over!!")
						state = 0


	# Render Code
	background.fill((0,0,0))
	pygame.Surface.blit(surf_board,IMAGES[2],(0,0))
	for x in range(0,7):
		for y in range(0,6):
			if board[x][y] == 0 and y == 0:
				column_num = font.render(str(x + 1), True, (0,0,0))
				text_coord = column_num.get_rect(center=(x*100 + 50, y*100 + 50))
				pygame.Surface.blit(surf_board, column_num, text_coord)
			elif board[x][y] != 0:
				coord = pygame.Rect(x * 100, y * 100, 100, 100)
				pygame.Surface.blit(surf_board,IMAGES[int(-(board[x][y] - 1) / 2)], coord)

	if state == 0:
		menu_text = font.render("Press SPACE to begin a new game", True, (255,255,255),(0,0,0))	
		menu_coord = menu_text.get_rect(center=(350,300))
		pygame.Surface.blit(surf_board, menu_text, menu_coord)
	else:
		pygame.Surface.blit(background,IMAGES[int(-(current_turn-1)/2)], (7*100, 0))


	pygame.Surface.blit(window,background, (0,0))
	pygame.Surface.blit(window,surf_board, (0,0))

	pygame.display.update()