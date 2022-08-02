from tkinter import W
import pygame
import random
import sys, os
import copy
import time

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

total_time = 0

def copy_board(test_board):
	return [x[:] for x in test_board] 

def drop_piece(test_board, column, type):
	for i in range(5,-1,-1):
		if test_board[column][i] == 0:
			test_board[column][i] = type
			return i + 1
	return 0


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

def fast_check(test_board, last_x, last_y):
	#Vertical
	if last_y >-1 and last_y < 3 and test_board[last_x][last_y+0] == test_board[last_x][last_y+1] == test_board[last_x][last_y+2] == test_board[last_x][last_y+3]:
		return test_board[last_x][last_y]
	if last_y > 0 and last_y < 4 and test_board[last_x][last_y-1] == test_board[last_x][last_y+0] == test_board[last_x][last_y+1] == test_board[last_x][last_y+2]:
		return test_board[last_x][last_y]
	if last_y > 1 and last_y < 5 and test_board[last_x][last_y-2] == test_board[last_x][last_y-1] == test_board[last_x][last_y+0] == test_board[last_x][last_y+1]:
		return test_board[last_x][last_y]
	if last_y > 2 and last_y < 5 and test_board[last_x][last_y-3] == test_board[last_x][last_y-2] == test_board[last_x][last_y-1] == test_board[last_x][last_y+0]:
		return test_board[last_x][last_y]
	#Horizontal
	if  last_x >-1 and last_x < 4 and test_board[last_x+0][last_y] == test_board[last_x+1][last_y] == test_board[last_x+2][last_y] == test_board[last_x+3][last_y]:
		return test_board[last_x][last_y]
	if last_x > 0 and last_x < 5 and test_board[last_x-1][last_y] == test_board[last_x+0][last_y] == test_board[last_x+1][last_y] == test_board[last_x+2][last_y]:
		return test_board[last_x][last_y]
	if last_x > 1 and last_x < 6 and test_board[last_x-2][last_y] == test_board[last_x-1][last_y] == test_board[last_x+0][last_y] == test_board[last_x+1][last_y]:
		return test_board[last_x][last_y]
	if last_x > 2 and                test_board[last_x-3][last_y] == test_board[last_x-2][last_y] == test_board[last_x-1][last_y] == test_board[last_x+0][last_y]:
		return test_board[last_x][last_y]
	#Diagonal Down
	if last_x >-1 and last_x < 4 and last_y >-1 and last_y < 3 and test_board[last_x+0][last_y+0] == test_board[last_x+1][last_y+1] == test_board[last_x+2][last_y+2] == test_board[last_x+3][last_y+3]:
		return test_board[last_x][last_y]
	if last_x > 0 and last_x < 5 and last_y > 0 and last_y < 4 and test_board[last_x-1][last_y-1] == test_board[last_x+0][last_y+0] == test_board[last_x+1][last_y+1] == test_board[last_x+2][last_y+2]:
		return test_board[last_x][last_y]
	if last_x > 1 and last_x < 6 and last_y > 1 and last_y < 5 and test_board[last_x-2][last_y-2] == test_board[last_x-1][last_y-1] == test_board[last_x+0][last_y+0] == test_board[last_x+1][last_y+1]:
		return test_board[last_x][last_y]
	if last_x > 2 and last_x < 7 and last_y > 2 and last_y < 6 and test_board[last_x-3][last_y-3] == test_board[last_x-2][last_y-2] == test_board[last_x-1][last_y-1] == test_board[last_x+0][last_y+0]:
		return test_board[last_x][last_y]
	#Diagonal Up
	if last_x >-1 and last_x < 4 and last_y > 2 and last_y < 6 and test_board[last_x+0][last_y+0] == test_board[last_x+1][last_y-1] == test_board[last_x+2][last_y-2] == test_board[last_x+3][last_y-3]:
		return test_board[last_x][last_y]
	if last_x > 0 and last_x < 5 and last_y > 1 and last_y < 5 and test_board[last_x-1][last_y+1] == test_board[last_x+0][last_y+0] == test_board[last_x+1][last_y-1] == test_board[last_x+2][last_y-2]:
		return test_board[last_x][last_y]
	if last_x > 1 and last_x < 6 and last_y > 0 and last_y < 4 and test_board[last_x-2][last_y+2] == test_board[last_x-1][last_y+1] == test_board[last_x+0][last_y+0] == test_board[last_x+1][last_y-1]:
		return test_board[last_x][last_y]
	if last_x > 2 and last_x < 7 and last_y >-1 and last_y < 3 and test_board[last_x-3][last_y+3] == test_board[last_x-2][last_y+2] == test_board[last_x-1][last_y+1] == test_board[last_x+0][last_y+0]:
		return test_board[last_x][last_y]

	return 0

board_cache = {}

def eval_position(test_board, last_x, last_y):
	global total_time
	cache_key = tuple(map(tuple, test_board))

	if cache_key in board_cache:
		return board_cache[cache_key]
	
	eval = 1000 * fast_check(test_board, last_x, last_y)
	board_cache[cache_key] = eval
	return eval


eval_count = 0

def search_move(test_board, test_turn, alpha, beta, depth, last_x, last_y):
	global eval_count, total_time
	eval_count += 1

	start_time = time.perf_counter()
	eval = eval_position(test_board, last_x, last_y)
	total_time += time.perf_counter() - start_time

	if depth == 0 or abs(eval) == 1000:
		return eval

	# otherwise check possible options until depth is reached

	if test_turn == 1:
		for i in range(0,7):
			if test_board[i][0] == 0:
				board_copy = copy_board(test_board)

				drop_height = drop_piece(board_copy, i, test_turn) - 1
				eval_value = search_move(board_copy, test_turn * -1, alpha, beta, depth - 1, i, drop_height)

				if eval_value >= beta:
					return beta
				if eval_value > alpha:
					alpha = eval_value
		return 0.99 * alpha
	elif test_turn == -1:
		for i in range(0,7):
			if test_board[i][0] == 0:
				board_copy = copy_board(test_board)

				drop_height = drop_piece(board_copy, i, test_turn) - 1
				eval_value = search_move(board_copy, test_turn * -1, alpha, beta, depth - 1, i, drop_height)

				if eval_value <= alpha:
					return alpha
				if eval_value < beta:
					beta = eval_value
		return 0.99 * beta


def generate_move(test_board, test_turn):
	#for i in range(0,7):
	#	copy_board = copy.deepcopy(board)
	#	drop_piece(copy_board, i, test_turn)
	#	if eval_board(copy_board, test_turn, 5) < 0:
	#		return i
	global eval_count, total_time
	eval_count = 0	

	start_time = time.perf_counter()
	total_time = 0

	# Avoid waits for forced moves
	#for i in range(0,7):
	#	board_copy = copy_board(test_board)
	#	drop_height = drop_piece(board_copy, i, test_turn) - 1

	#	if fast_check(board_copy, i, drop_height):
	#		return i

	#for i in range(0,7):	
	#	board_copy = copy_board(test_board)
	#	drop_height = drop_piece(board_copy, i, -1 * test_turn) - 1

	#	if fast_check(board_copy, i, drop_height):
	#		return i
		

	evals = []
	for i in range(0,7):
		if test_board[i][0] != 0:
			evals.append(10000)
		else:
			board_copy = copy_board(test_board)
			drop_height = drop_piece(board_copy, i, test_turn) - 1

			evals.append(search_move(board_copy, test_turn * -1, -10000, 10000, 8, i, drop_height)) #Time testing with 7


	target = 1000
	index = -1

	print(evals)
	shuffled_range = random.sample(range(0,7), 7)
	for i in shuffled_range:
		if evals[i] < target:
			target = evals[i]
			index = i
		
	duration = time.perf_counter() - start_time
	print("Evaluation Count:  " + str(eval_count) + "   " + str(total_time) + " in " + str(duration))

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