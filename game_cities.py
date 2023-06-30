import sys, os
import pygame

from game_helpers import scale_tuple, Spritesheet

from pygame.locals import (
	K_ESCAPE,
	BUTTON_LEFT,

	KEYDOWN,
	MOUSEBUTTONDOWN,
	QUIT
)

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800 

def main():
	pygame.display.init()
	
	window = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.RESIZABLE)
	screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

	clock = pygame.time.Clock()

	pygame.display.set_caption("Dan's City Simulator!")


	module = sys.modules['__main__']
	path, name = os.path.split(module.__file__)

	sheet_city = Spritesheet(os.path.join(path, "res", "city", "city_tiles.png"), 16, 16)
	tex_road = sheet_city.image_from_index(0, 0, (255, 0, 255))

	markers = []

	# Dictionary representing the road grid
	roads = {}	
	for x in range(0,20):
		for y in range(0,30):
			roads[(x,y)] = 2 + x*y // 12
	
	running = True
	while running:
		# Event Handler
		events = pygame.event.get()
		for event in events:
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					running = False
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == BUTTON_LEFT:
					mouse_pos = pygame.mouse.get_pos()
					markers.append((mouse_pos[0], mouse_pos[1]))
			elif event.type == pygame.MOUSEWHEEL:
				pass
			elif event.type == QUIT:
				running = False

		screen.fill((200,0,0))

		for mark in markers:
			#pygame.draw.rect(screen,(0,255,255),(mark[0] - 10, mark[1] - 10, 20,20))
			screen.blit(tex_road, (mark[0] - 10, mark[1] - 10, 20,20))
		if len(markers) > 1:
			pygame.draw.aalines(screen, (0,255,255), True, markers)

		for road in roads:
			start = (road[0], road[1] // 2)
			if road[1] % 2 == 0:
				end = (road[0] + 1, road[1] // 2)
			else:
				end = (road[0], road[1] // 2 + 1)

			start = scale_tuple(50, start)		
			end = scale_tuple(50, end)
			pygame.draw.lines(screen, (0,0,0), False, [start, end], width = roads[road])

		pygame.transform.scale(screen, window.get_size(), dest_surface=window)
		
		pygame.display.flip()
		clock.tick(120)

	pygame.display.quit()
	pygame.quit()
	sys.exit()


if __name__ == '__main__':
	main()	