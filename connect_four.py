from turtle import back
import pygame

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

pygame.init()

pygame.display.set_caption("Connect 4")
window = pygame.display.set_mode((800,600))

background = pygame.Surface((800,600))
background.fill((0,0,0))


board = [[2 for y in range(6)] for x in range(7)] 


def drop_piece(column, type):
	for i in range(5,-1,-1):
		if board[column][i] == 2:
			board[column][i] = type
			return True
	return False

running = True
alive = True

current_turn = 0
while running:
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False
		if event.type == KEYDOWN:	
			if event.key in range(K_1,K_7+1) and drop_piece(event.key - K_1, current_turn):
				current_turn = (current_turn + 1) % 2



	print(K_2)


	# Render Code
	for x in range(0,7):
		for y in range(0,6):
			coord = pygame.Rect(x * 100, y * 100, 100, 100)
			if board[x][y] == 0:
				background.fill((255,255,0),coord)
			elif board[x][y] == 1:
				background.fill((255,0,0),coord)
			elif board[x][y] == 2:
				background.fill((128,128,128),coord)

	window.blit(background, (0,0))

	pygame.display.update()