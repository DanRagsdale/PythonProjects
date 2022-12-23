import sys, os
import pygame
from pygame.locals import *
import random
import time

from PIL import Image

pygame.init()

vec = pygame.math.Vector2

WIDTH = 1400
HEIGHT = 900
FPS = 120

ACC = 0.5
FRIC = -0.1
GRAVITY = 0.25

BLOCK_SIZE = 50

clock = pygame.time.Clock()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

module = sys.modules['__main__']
path, name = os.path.split(module.__file__)

tex_dirt = pygame.image.load(os.path.join(path, "res", "platformer", "textures", "tex_dirt.png"))
tex_dirt.convert()

tex_player = pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "player_idle_00.png"))
tex_player.convert()


class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
		self.surf.fill((255,0,0))
		self.rect = self.surf.get_rect(topleft=(x,y))

		self.texture = tex_dirt 


class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.surf = pygame.Surface((BLOCK_SIZE * 0.8, 0.8 * 2 * BLOCK_SIZE))
		self.surf.fill((128,64,32))
		self.rect = self.surf.get_rect()

		self.pos = vec(BLOCK_SIZE / 2 , 385)
		self.vel = vec(0,0)
		self.acc = vec(0,0)

		self.jump_counter = 0
		self.on_ground = 0
		self.col_distances = (0,0,0,0)
		
		self.texture = tex_player 


	def move(self):
		true_grav = GRAVITY	

		pressed_keys = pygame.key.get_pressed()
		if pressed_keys[K_SPACE]:
			true_grav = GRAVITY / 2
			if self.jump_counter > 0:
				self.vel.y += -0.3
				self.jump_counter -= 1
		else:
			self.jump_counter = 0

		self.acc = vec(0,true_grav)

		if pressed_keys[K_LEFT] and not pressed_keys[K_RIGHT]:
			self.acc.x = -ACC
		if pressed_keys[K_RIGHT] and not pressed_keys[K_LEFT]:
			self.acc.x = ACC

		self.acc.x += self.vel.x * (FRIC)

		self.vel += self.acc
		
		# Constrain velocity based on raycasts
		self.update_distances()

		self.vel.y = max(min(self.vel.y, self.col_distances[2]), -self.col_distances[3])
		print(self.col_distances[3])


		self.pos += self.vel
		self.rect.midbottom = self.pos

	def update_distances(self):
		#Raycast downward
		down_dists = [100000]

		for test_plat in platforms:
			if self.rect.bottom <= test_plat.rect.top + 2:
				if test_plat.rect.left < self.rect.left < test_plat.rect.right:
					down_dists.append(max(test_plat.rect.top - self.rect.bottom, 0))
				if test_plat.rect.left < self.rect.centerx < test_plat.rect.right:
					down_dists.append(max(test_plat.rect.top - self.rect.bottom, 0))
				if test_plat.rect.left < self.rect.right < test_plat.rect.right:
					down_dists.append(max(test_plat.rect.top - self.rect.bottom, 0))

		#Raycast upward
		up_dists = [100000]
		
		for test_plat in platforms:
			if self.rect.top >= test_plat.rect.bottom - 2:
				if test_plat.rect.left < self.rect.left < test_plat.rect.right:
					up_dists.append(max(self.rect.top - test_plat.rect.bottom, 0))
				if test_plat.rect.left < self.rect.centerx < test_plat.rect.right:
					up_dists.append(max(self.rect.top - test_plat.rect.bottom, 0))
				if test_plat.rect.left < self.rect.right < test_plat.rect.right:
					up_dists.append(max(self.rect.top - test_plat.rect.bottom, 0))


		self.col_distances = (0,0, min(down_dists), min(up_dists))

	def set_on_ground(self):
		if self.col_distances[0] < 5:
			self.on_ground = 5

		self.on_ground -= 1
			

	def jump(self):
		if self.on_ground > 0:
			self.vel.y = -4.5
			self.jump_counter = 10

	def update(self):
		#ground_hits = pygame.sprite.spritecollide(self, platforms, False)
		#for hit in ground_hits:
		#	delta = (self.rect.center[0] - hit.rect.center[0], self.rect.center[1] - hit.rect.center[1])
		#	if abs(delta[1]) - 1.5*abs(delta[0]) > 2:
		#		if delta [1] < 0 and self.vel.y > 0:
		#			self.pos.y = hit.rect.top + 1
		#			self.vel.y = 0
		#		elif delta[1] > 0:
		#			self.pos.y = hit.rect.bottom + 2*BLOCK_SIZE
		#			self.vel.y = 0

		wall_hits = pygame.sprite.spritecollide(self, platforms, False)
		for hit in wall_hits:
			delta = (self.rect.center[0] - hit.rect.center[0], self.rect.center[1] - hit.rect.center[1])
			if 1.5*abs(delta[0]) - abs(delta[1]) > 3:
				if delta[0] > 0:
					self.pos.x = hit.rect.right + BLOCK_SIZE / 2 - 1
				else:
					self.pos.x = hit.rect.left - BLOCK_SIZE / 2 + 1
				self.vel.x = 0




player = Player()

all_sprites = pygame.sprite.Group()
all_sprites.add(player)

platforms = pygame.sprite.Group()

img = Image.open(os.path.join(path, "res", "platformer", "level_001.png"))
print(img.format, img.size, img.mode)
for x in range(img.size[0]):
	for y in range(img.size[1]):
		pixel = img.getpixel((x,y))
		if pixel != (0,0,0):
			plat = Platform(x * BLOCK_SIZE, y * BLOCK_SIZE)

			all_sprites.add(plat)
			platforms.add(plat)

game_map = pygame.Surface((img.size[0] * BLOCK_SIZE, img.size[1] * BLOCK_SIZE))
background = pygame.Surface((img.size[0] * BLOCK_SIZE, img.size[1] * BLOCK_SIZE))

for entity in platforms:
	background.blit(tex_dirt, entity.rect)

window_pos = [0,0]

last_time = 0

frame_count = 0
running = True
while running:
	# Game Code
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False
		elif event.type == KEYDOWN:
			if event.key == K_SPACE:
				player.jump()

	player.move()
	player.update()
	player.set_on_ground()

	# Rendering Code
	if player.pos.x > (-window_pos[0] + WIDTH * 0.7):
		window_pos[0] -= abs(player.vel.x)
	if player.pos.x < (-window_pos[0] + WIDTH * 0.2) and player.pos.x > WIDTH * 0.2:
		window_pos[0] += abs(player.vel.x)

	# Close if player dies
	if player.pos.y > HEIGHT + 1:
		running = False

	if frame_count % 1 == 0:
		game_map.fill((0,0,0))
		game_map.blit(background, (0,0))
		#game_map.blit(player.texture, player.rect)
		game_map.blit(player.surf, player.rect)

		window.fill((0,0,0))
		window.blit(game_map, window_pos)

		pygame.display.update()

	current_time = time.perf_counter()
	frame_time = current_time - last_time
	#print("Frame time is: ", str(frame_time), "s or ", str(1/frame_time), "FPS")

	last_time = current_time

	frame_count += 1
	clock.tick(FPS)

pygame.quit()
sys.exit()