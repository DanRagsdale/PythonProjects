import sys, os
import pygame
from pygame.locals import *
import random
import time

from PIL import Image

pygame.init()

vec = pygame.math.Vector2

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
TICK_RATE = 60
ANIM_RATE = 5

ACC = 0.5
MAX_SPEED = 10
FRIC = -0.2
JUMP_VEL = -20
GRAVITY = 2

BLOCK_SIZE = 50

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

clock = pygame.time.Clock()

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")

module = sys.modules['__main__']
path, name = os.path.split(module.__file__)


pygame.display.set_caption("Platformer Creator")
font = pygame.font.SysFont("Arial Black", 30)

tex_dirt = pygame.image.load(os.path.join(path, "res", "platformer", "textures", "tex_dirt.png"))
tex_block = pygame.image.load(os.path.join(path, "res", "platformer", "textures", "tex_block.png"))

tex_coin = [
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "coin-00.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "coin-01.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "coin-02.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "coin-03.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "coin-04.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "coin-05.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "coin-06.png")).convert_alpha(),
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "coin-07.png")).convert_alpha(),
]

tex_idle = [
	pygame.image.load(os.path.join(path, "res", "platformer", "sprites", "adventurer-idle-00.png")).convert_alpha(),
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
	def __init__(self, x, y, texture):
		super().__init__()
		self.surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
		self.surf.fill((255,0,0))
		self.rect = self.surf.get_rect(topleft=(x,y))

		self.texture = texture

class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		
		self.surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
		self.surf.fill((255,255,0))
		self.rect = self.surf.get_rect(topleft=(x,y))

		self.texture = tex_coin[0]
		self.anim_index = 0

	def update(self, game):
		collisions = pygame.sprite.spritecollide(self, game.entities, False)
		for col in collisions:
			if isinstance(col, Player):
				game.score += 100
				self.kill()

	def update_anims(self, game):
		self.anim_index += 1
		texture_list = tex_coin

		if self.anim_index >= len(texture_list):
			self.anim_index = 0
		self.texture = texture_list[self.anim_index]

class Player(pygame.sprite.Sprite):
	class State:
		Idle, Running = range(2)
		Textures = {Idle:tex_idle, Running:tex_run}

	def __init__(self, start_pos):
		super().__init__()
		self.surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
		self.surf.fill((128,64,32))
		self.rect = self.surf.get_rect()

		self.pos = start_pos
		self.rect.midbottom = self.pos
		self.vel = vec(0,0)
		self.acc = vec(0,0)

		self.on_ground = 0
		self.col_distances = (0,0,0,0)

		self.direction = True
		self.current_state = Player.State.Idle
		self.anim_index = 0

		self.texture = tex_idle[0]

	def move(self, game):
		true_grav = GRAVITY	

		pressed_keys = pygame.key.get_pressed()
		if pressed_keys[K_SPACE]:
			true_grav = GRAVITY / 3

		self.acc = vec(0,true_grav)

		if pressed_keys[K_LEFT] and not pressed_keys[K_RIGHT]:
			self.direction = False
			self.acc.x = -ACC
		elif pressed_keys[K_RIGHT] and not pressed_keys[K_LEFT]:
			self.direction = True
			self.acc.x = ACC
		else:
			self.acc.x += self.vel.x * (FRIC)

		self.vel += self.acc
		self.vel.x = max(min(self.vel.x, MAX_SPEED), -MAX_SPEED)
		
		# Constrain velocity based on raycasts
		self.update_distances(game)

		self.vel.y = max(min(self.vel.y, self.col_distances[3]), -self.col_distances[2])
		self.vel.x = max(min(self.vel.x, self.col_distances[1]), -self.col_distances[0])
		#print(self.col_distances[2])

		if abs(self.vel.x) > 0.2:
			self.current_state = Player.State.Running
		else:
			self.current_state = Player.State.Idle

		self.pos += self.vel
		self.rect.midbottom = self.pos

	def jump(self):
		if self.on_ground > 0:
			self.vel.y = JUMP_VEL

	def update(self, game):
		self.set_on_ground()

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

	def update_anims(self, game):
		self.anim_index += 1
		texture_list = Player.State.Textures[self.current_state]

		if self.anim_index >= len(texture_list):
			self.anim_index = 0
		if self.direction:
			self.texture = texture_list[self.anim_index]
		else:
			self.texture = pygame.transform.flip(texture_list[self.anim_index], True, False)

	def update_distances(self, game):
		#Raycast upward
		up_dists = [100000]
		
		for test_plat in game.platforms:
			if self.rect.top >= test_plat.rect.bottom - 2:
				if test_plat.rect.left < self.rect.left < test_plat.rect.right:
					up_dists.append(max(self.rect.top - test_plat.rect.bottom, 0))
				if test_plat.rect.left < self.rect.centerx < test_plat.rect.right:
					up_dists.append(max(self.rect.top - test_plat.rect.bottom, 0))
				if test_plat.rect.left < self.rect.right < test_plat.rect.right:
					up_dists.append(max(self.rect.top - test_plat.rect.bottom, 0))

		#Raycast downward
		down_dists = [100000]

		for test_plat in game.platforms:
			if self.rect.bottom <= test_plat.rect.top + 2:
				if test_plat.rect.left < self.rect.left < test_plat.rect.right:
					down_dists.append(max(test_plat.rect.top - self.rect.bottom, 0))
				if test_plat.rect.left < self.rect.centerx < test_plat.rect.right:
					down_dists.append(max(test_plat.rect.top - self.rect.bottom, 0))
				if test_plat.rect.left < self.rect.right < test_plat.rect.right:
					down_dists.append(max(test_plat.rect.top - self.rect.bottom, 0))

		#Raycast left
		left_dists = [100000]
		
		for test_plat in game.platforms:
			if self.rect.left >= test_plat.rect.right - 2:
				if test_plat.rect.top < self.rect.top < test_plat.rect.bottom:
					left_dists.append(max(self.rect.left - test_plat.rect.right, 0))
				
				if test_plat.rect.top < self.rect.centery < test_plat.rect.bottom:
					left_dists.append(max(self.rect.left - test_plat.rect.right, 0))
				
				if test_plat.rect.top < self.rect.bottom < test_plat.rect.bottom:
					left_dists.append(max(self.rect.left - test_plat.rect.right, 0))
		
		#Raycast right
		right_dists = [100000]
		
		for test_plat in game.platforms:
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
			

class Game():
	def __init__(self):
		self.map_names = os.listdir(os.path.join(path, "res", "platformer", "maps"))
		self.map_names.sort()
		print(self.map_names)

		self.main_loop()


	def load_level(self, level_name):

		START_POS = vec(0,0)

		self.platforms = pygame.sprite.Group()
		self.entities = pygame.sprite.Group()

		img = Image.open(os.path.join(path, "res", "platformer", "maps", level_name))
		for x in range(img.size[0]):
			for y in range(img.size[1]):
				pixel = img.getpixel((x,y))[0:3] #Ignore pixel alpha channel

				if pixel != (0,0,0):
					if pixel == (0xff,0,0):
						START_POS = vec(x * BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE -2)
					elif pixel == (0xff,0xff,0):
						coin = Coin(x * BLOCK_SIZE, y * BLOCK_SIZE)
						self.entities.add(coin)
					elif pixel == (0x88,0x88,0x88):
						plat = Platform(x * BLOCK_SIZE, y * BLOCK_SIZE, tex_block)
						self.platforms.add(plat)
					else:
						plat = Platform(x * BLOCK_SIZE, y * BLOCK_SIZE, tex_dirt)
						self.platforms.add(plat)

		self.player = Player(START_POS)
		self.entities.add(self.player)

		self.game_map = pygame.Surface((img.size[0] * BLOCK_SIZE, img.size[1] * BLOCK_SIZE))
		self.background = pygame.Surface((img.size[0] * BLOCK_SIZE, img.size[1] * BLOCK_SIZE))
		self.background.fill((100,100,220))

		for plat in self.platforms:
			self.background.blit(plat.texture, plat.rect)

		self.window_pos = [0,0]
		self.score = 0




	def main_loop(self):
		last_frame = last_physics = last_anim = time.perf_counter()
		state = 0
		frame_count = 0
		running = True

		self.load_level(self.map_names[0])

		self.gui = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.gui.set_colorkey((255,0,255))

		self.scroll_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.scroll_surf.set_colorkey((255,0,255))

		start_buttons = []
		for i in range(0, len(self.map_names)):
			button = pygame.Rect(0,SCREEN_HEIGHT / 3 + i * 100,160,80)
			start_buttons.append(button)

		while running:
			current_time = time.perf_counter()

			if (current_time - last_frame) > 1.0 / 60:
				print("Stuttering")


			mouse_pos = pygame.mouse.get_pos()

			# Update Game
			if state == 0:
				for event in pygame.event.get():
					if event.type == QUIT:
						running = False
					elif event.type == MOUSEBUTTONDOWN and event.button == 1:
						for i, button in enumerate(start_buttons):
							if button.collidepoint(mouse_pos[0], mouse_pos[1]):
								self.load_level(self.map_names[i])
								state = 1
					elif event.type == MOUSEWHEEL:
						for button in start_buttons:
							button.centery += 10 * event.y
			else:
				while current_time - last_physics > 1.0 / TICK_RATE:
					for event in pygame.event.get():
						if event.type == QUIT:
							running = False
						elif event.type == KEYDOWN:
							if event.key == K_SPACE:
								self.player.jump()

					self.player.move(self)

					for entity in self.entities:
						entity.update(self)

					last_physics += 1.0 / TICK_RATE
				
					# Close if player dies
				if self.player.pos.y > SCREEN_HEIGHT + PLAYER_HEIGHT + 1:
					state = 0
			
			#Update Animations
			if current_time - last_anim > 1.0 / ANIM_RATE:
				for entity in self.entities:
					entity.update_anims(self)
				last_anim = current_time

			# Rendering Code
			if self.player.pos.x > (-self.window_pos[0] + SCREEN_WIDTH * 0.7):
				self.window_pos[0] -= abs(self.player.vel.x)
			if self.player.pos.x < (-self.window_pos[0] + SCREEN_WIDTH * 0.2) and self.player.pos.x > SCREEN_WIDTH * 0.2:
				self.window_pos[0] += abs(self.player.vel.x)
	
			
			self.gui.fill((255,0,255))
			score_text = font.render('Score: ' + str(self.score), False, (255,255,255))
			pygame.Surface.blit(self.gui,score_text, (1 * BLOCK_SIZE, 1 * BLOCK_SIZE))

			self.scroll_surf.fill((255,0,255))

			if state == 0:
				# Blit menu GUI
				for button in start_buttons:
					pygame.Surface.fill(self.scroll_surf, (128,128,128), button)
				self.scroll_surf.fill((255,0,255),(0,0, SCREEN_WIDTH, SCREEN_HEIGHT / 3))

				pygame.Surface.blit(self.gui, self.scroll_surf, (0,0))


			self.game_map.fill((100,100,220))
			self.game_map.blit(self.background, (0,0))
	
			for entity in self.entities:
				self.game_map.blit(entity.texture, entity.rect)



			window.fill((0,0,0))
			window.blit(self.game_map, self.window_pos)
			window.blit(self.gui, (0,0))

			pygame.display.update()

			last_frame = current_time
			frame_count += 1

		pygame.display.quit()
		pygame.quit()
		sys.exit()

if __name__ == '__main__':
	game = Game()