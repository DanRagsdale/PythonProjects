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
TICK_RATE = 60
ANIM_RATE = 5

ACC = 2
FRIC = -0.2
JUMP_VEL = -20
GRAVITY = 2

BLOCK_SIZE = 50

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

clock = pygame.time.Clock()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

module = sys.modules['__main__']
path, name = os.path.split(module.__file__)

tex_dirt = pygame.image.load(os.path.join(path, "res", "platformer", "textures", "tex_dirt.png"))

tex_player = pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "player_idle_00.tga"))
#tex_player.convert()


tex_idle = [
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "adventurer-idle-00.tga")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "adventurer-idle-01.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "adventurer-idle-02.png")).convert_alpha(),
]

tex_run = [
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "adventurer-run-00.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "adventurer-run-01.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "adventurer-run-02.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "adventurer-run-03.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "adventurer-run-04.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "adventurer-run-05.png")).convert_alpha(),
]


class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
		self.surf.fill((255,0,0))
		self.rect = self.surf.get_rect(topleft=(x,y))

		self.texture = tex_dirt 

START_POS = vec(BLOCK_SIZE / 2 , 385)

class Player(pygame.sprite.Sprite):
	class State:
		Idle, Running = range(2)
		Textures = {Idle:tex_idle, Running:tex_run}

	def __init__(self):
		super().__init__()
		self.surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
		self.surf.fill((128,64,32))
		self.rect = self.surf.get_rect()

		self.pos = START_POS
		self.vel = vec(0,0)
		self.acc = vec(0,0)

		self.on_ground = 0
		self.col_distances = (0,0,0,0)

		self.direction = True
		self.current_state = Player.State.Idle
		self.anim_index = 0

		self.texture = tex_idle[0]


	def move(self):
		true_grav = GRAVITY	

		pressed_keys = pygame.key.get_pressed()
		if pressed_keys[K_SPACE]:
			true_grav = GRAVITY / 3

		self.acc = vec(0,true_grav)

		if pressed_keys[K_LEFT] and not pressed_keys[K_RIGHT]:
			self.direction = False
			self.acc.x = -ACC
		if pressed_keys[K_RIGHT] and not pressed_keys[K_LEFT]:
			self.direction = True
			self.acc.x = ACC

		self.acc.x += self.vel.x * (FRIC)

		self.vel += self.acc
		
		# Constrain velocity based on raycasts
		self.update_distances()

		self.vel.y = max(min(self.vel.y, self.col_distances[3]), -self.col_distances[2])
		self.vel.x = max(min(self.vel.x, self.col_distances[1]), -self.col_distances[0])
		#print(self.col_distances[2])

		if abs(self.vel.x) > 0.2:
			self.current_state = Player.State.Running
		else:
			self.current_state = Player.State.Idle

		self.pos += self.vel
		self.rect.midbottom = self.pos

	def update_anims(self):
		self.anim_index += 1
		texture_list = Player.State.Textures[self.current_state]

		if self.anim_index >= len(texture_list):
			self.anim_index = 0
		if self.direction:
			self.texture = texture_list[self.anim_index]
		else:
			self.texture = pygame.transform.flip(texture_list[self.anim_index], True, False)


	def update_distances(self):
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

		#Raycast left
		left_dists = [100000]
		
		for test_plat in platforms:
			if self.rect.left >= test_plat.rect.right - 2:
				if test_plat.rect.top < self.rect.top < test_plat.rect.bottom:
					left_dists.append(max(self.rect.left - test_plat.rect.right, 0))
				
				if test_plat.rect.top < self.rect.centery < test_plat.rect.bottom:
					left_dists.append(max(self.rect.left - test_plat.rect.right, 0))
				
				if test_plat.rect.top < self.rect.bottom < test_plat.rect.bottom:
					left_dists.append(max(self.rect.left - test_plat.rect.right, 0))
		
		#Raycast right
		right_dists = [100000]
		
		for test_plat in platforms:
			if self.rect.right <= test_plat.rect.left + 2:
				if test_plat.rect.top < self.rect.top < test_plat.rect.bottom:
					right_dists.append(max(test_plat.rect.left - self.rect.right, 0))
				if test_plat.rect.top < self.rect.centery < test_plat.rect.bottom:
					right_dists.append(max(test_plat.rect.left - self.rect.right, 0))
				if test_plat.rect.top < self.rect.bottom < test_plat.rect.bottom:
					right_dists.append(max(test_plat.rect.left - self.rect.right, 0))


		self.col_distances = (min(left_dists), min(right_dists), min(up_dists), min(down_dists))

	def set_on_ground(self):
		if self.col_distances[3] < 5:
			self.on_ground = 5

		self.on_ground -= 1
			

	def jump(self):
		if self.on_ground > 0:
			self.vel.y = JUMP_VEL

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

		#wall_hits = pygame.sprite.spritecollide(self, platforms, False)
		#for hit in wall_hits:
		#	delta = (self.rect.center[0] - hit.rect.center[0], self.rect.center[1] - hit.rect.center[1])
		#	if 1.5*abs(delta[0]) - abs(delta[1]) > 3:
		#		if delta[0] > 0:
		#			self.pos.x = hit.rect.right + BLOCK_SIZE / 2 - 1
		#		else:
		#			self.pos.x = hit.rect.left - BLOCK_SIZE / 2 + 1
		#		self.vel.x = 0
		pass


all_sprites = pygame.sprite.Group()

platforms = pygame.sprite.Group()

img = Image.open(os.path.join(path, "res", "platformer", "level_002.png"))
for x in range(img.size[0]):
	for y in range(img.size[1]):
		pixel = img.getpixel((x,y))[0:3] #Ignore pixel alpha channel

		if pixel != (0,0,0):
			if pixel == (0xff,0,0):
				START_POS = vec(x * BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE -2)
			else:
				plat = Platform(x * BLOCK_SIZE, y * BLOCK_SIZE)
				all_sprites.add(plat)
				platforms.add(plat)

player = Player()
all_sprites.add(player)

game_map = pygame.Surface((img.size[0] * BLOCK_SIZE, img.size[1] * BLOCK_SIZE))
background = pygame.Surface((img.size[0] * BLOCK_SIZE, img.size[1] * BLOCK_SIZE))
background.fill((100,100,220))

for entity in platforms:
	background.blit(tex_dirt, entity.rect)

window_pos = [0,0]

last_frame = last_physics = last_anim = time.perf_counter()

frame_count = 0
running = True
while running:
	current_time = time.perf_counter()

	# Game Code
	while current_time - last_physics > 1.0 / TICK_RATE:
		for event in pygame.event.get():
			if event.type == QUIT:
				running = False
			elif event.type == KEYDOWN:
				if event.key == K_SPACE:
					player.jump()

		player.move()
		player.update()
		player.set_on_ground()

		last_physics += 1.0 / TICK_RATE
	
	if current_time - last_anim > 1.0 / ANIM_RATE:
		player.update_anims()
		last_anim = current_time

	# Close if player dies
	if player.pos.y > HEIGHT + 1:
		running = False

	# Rendering Code
	if player.pos.x > (-window_pos[0] + WIDTH * 0.7):
		window_pos[0] -= abs(player.vel.x)
	if player.pos.x < (-window_pos[0] + WIDTH * 0.2) and player.pos.x > WIDTH * 0.2:
		window_pos[0] += abs(player.vel.x)


	game_map.fill((100,100,220))
	game_map.blit(background, (0,0))
	game_map.blit(player.texture, player.rect)
	#game_map.blit(player.surf, player.rect)

	window.fill((0,0,0))
	window.blit(game_map, window_pos)

	pygame.display.update()

	last_frame = current_time
	frame_count += 1

pygame.quit()
sys.exit()