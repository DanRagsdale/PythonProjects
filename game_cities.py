import sys
import pygame

from pygame.locals import (
	K_ESCAPE,

	KEYDOWN,
	MOUSEBUTTONDOWN,
	QUIT
)

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800 


def main():
	pygame.display.init()
	
	window = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
	screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

	clock = pygame.time.Clock()

	pygame.display.set_caption("Dan's City Simulator!")

	markers = []	

	running = True
	while running:
		# Event Handler
		events = pygame.event.get()
		for event in events:
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					running = False
			elif event.type == MOUSEBUTTONDOWN:
				markers.append(pygame.mouse.get_pos())
			elif event.type == QUIT:
				running = False


		screen.fill((200,0,0))

		for mark in markers:
			pygame.draw.rect(screen,(0,255,255),(*mark, 10,10))

		pygame.Surface.blit(window, screen, (0,0))
		
		pygame.display.flip()
		clock.tick(120)

	pygame.display.quit()
	pygame.quit()
	sys.exit()


if __name__ == '__main__':
	main()	