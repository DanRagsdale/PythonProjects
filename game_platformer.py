import sys, os
import pygame
from pygame.locals import *
import random
import time
import math

from PIL import Image

from game_helpers import *

pygame.init()

vec = pygame.math.Vector2

BLOCK_SIZE = 48

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 18 * BLOCK_SIZE
TICK_RATE = 60
ANIM_RATE = 5

ACC = 0.5
MAX_SPEED = 10
FRIC = -0.2
JUMP_VEL = -20
GRAVITY = 2

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

clock = pygame.time.Clock()

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")

module = sys.modules['__main__']
path, name = os.path.split(module.__file__)


pygame.display.set_caption("Platformer Creator")
font = pygame.font.SysFont("Arial Black", 30)


sheet_player = Spritesheet(os.path.join(path, "res", "platformer", "sprites", "sheet_player.png"), PLAYER_WIDTH, PLAYER_HEIGHT)
tex_idle = sheet_player.load_strip(0, 3, (255,0,255))
tex_run = sheet_player.load_strip(1, 6, (255,0,255))

sheet_flag = Spritesheet(os.path.join(path, "res", "platformer", "sprites", "sheet_flag.png"), BLOCK_SIZE * 2, BLOCK_SIZE * 2)
tex_flag_up = sheet_flag.load_strip(0, 5, (255,0,255))
tex_flag_down = sheet_flag.load_strip(1, 5, (255,0,255))

sheet_coin = Spritesheet(os.path.join(path, "res", "platformer", "sprites", "sheet_coin.png"), BLOCK_SIZE, BLOCK_SIZE)
tex_coin = sheet_coin.load_strip(0, 8, (255,0,255))

sheet_crab = Spritesheet(os.path.join(path, "res", "platformer", "sprites", "sheet_crab.png"), BLOCK_SIZE, BLOCK_SIZE)
tex_crab = sheet_crab.load_strip(0, 2, (255,0,255))

sheet_textures = Spritesheet(os.path.join(path, "res", "platformer", "textures", "sheet_textures.png"), BLOCK_SIZE, BLOCK_SIZE)

tex_stone = sheet_textures.image_from_index(0, 0, (255,0,255))
tex_brick = sheet_textures.image_from_index(1, 0, (255,0,255))

tex_dirt = sheet_textures.image_from_index(0, 1, (255,0,255))
tex_dirt_l = sheet_textures.image_from_index(1, 1, (255,0,255))
tex_dirt_r = sheet_textures.image_from_index(2, 1, (255,0,255))

tex_grass = sheet_textures.image_from_index(0, 2, (255,0,255))
tex_grass_l = sheet_textures.image_from_index(1, 2, (255,0,255))
tex_grass_r = sheet_textures.image_from_index(2, 2, (255,0,255))

tex_cobble = sheet_textures.image_from_index(0, 3, (255,0,255))
tex_cobble_l = sheet_textures.image_from_index(1, 3, (255,0,255))
tex_cobble_r = sheet_textures.image_from_index(2, 3, (255,0,255))

class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, texture):
		super().__init__()
		self.surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
		self.surf.fill((255,0,0))
		self.rect = self.surf.get_rect(topleft=(x,y))

		self.texture = texture

class Flag(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		
		self.surf = pygame.Surface((2 * BLOCK_SIZE, 2 * BLOCK_SIZE))
		self.surf.fill((255,255,0))
		self.rect = self.surf.get_rect(topleft=(x,y-BLOCK_SIZE))

		self.texture = tex_flag_up[0]
		self.anim_index = 0

		self.state = 0

	def update(self, game):
		if self.state == 0:
			collisions = pygame.sprite.spritecollide(self, game.entities, False)
			for col in collisions:
				if isinstance(col, Player):
					game.score += 2000
					self.state = 1
					self.anim_index = 0


	def update_anims(self, game):
		self.anim_index += 1
		if self.state == 0:
			texture_list = tex_flag_up
			if self.anim_index >= len(texture_list):
				self.anim_index = 0
		else:
			texture_list = tex_flag_down
			if self.anim_index >= len(texture_list):
				self.anim_index = len(texture_list) - 1

		self.texture = texture_list[self.anim_index]

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

class Crab(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()

		self.surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
		self.surf.fill((255,255,0))
		self.rect = self.surf.get_rect(topleft=(x,y))

		self.texture = tex_crab[0]
		self.anim_index = 0

		self.dir = 1

	def update(self, game):
		grid_x = int(self.rect.centerx / BLOCK_SIZE)
		grid_y = int(self.rect.centery / BLOCK_SIZE)

		test_x = int(self.rect.centerx / BLOCK_SIZE + self.dir * 0.5)

		if (grid_y < len(game.solids_map[0]) - 1 and game.solids_map[grid_x][grid_y+1]==0) or (0 <= test_x < len(game.solids_map) and game.solids_map[test_x][grid_y]):
			self.dir *= -1

		self.rect.centerx += self.dir


	def update_anims(self, game):
		self.anim_index += 1
		texture_list = tex_crab

		if self.anim_index >= len(texture_list):
			self.anim_index = 0
		self.texture = texture_list[self.anim_index]

class Player(pygame.sprite.Sprite):
	class State:
		Idle, Running = range(2)
		Textures = {Idle:tex_idle, Running:tex_run}

		#print(check_ray_rect_collision((2,-1,1,0), pygame.Rect(1,0,2,2)))

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

		
		#leg = self.col_distances[5] * 0.707
		#print(leg, self.vel)
		#if self.vel.x > leg and self.vel.y > leg:
		#	print("Triggered: ", self.vel.x, self.vel.y)
		#	self.vel = vec(0,0)

		#print(self.col_distances)
		self.pos += self.vel
		self.rect.midbottom = self.pos

	def jump(self):
		if self.on_ground > 0:
			self.vel.y = JUMP_VEL

	def update(self, game):
		self.move(game)
		self.set_on_ground()
		
		collisions = pygame.sprite.spritecollide(self, game.entities, False)
		for col in collisions:
			if isinstance(col, Crab):
				if self.rect.bottom < col.rect.centery:
					game.score += 1000
					self.vel.y = JUMP_VEL
					col.kill()

	def update_anims(self, game):
		if abs(self.vel.x) > 0.2:
			self.current_state = Player.State.Running
		else:
			self.current_state = Player.State.Idle

		self.anim_index += 1
		texture_list = Player.State.Textures[self.current_state]

		if self.anim_index >= len(texture_list):
			self.anim_index = 0
		if self.direction:
			self.texture = texture_list[self.anim_index]
		else:
			self.texture = pygame.transform.flip(texture_list[self.anim_index], True, False)

	def update_distances(self, game):
		offset = 1

		grid_x = int(self.rect.centerx / BLOCK_SIZE)
		grid_y = int(self.rect.centery / BLOCK_SIZE)

		up_dists = [float('inf')]
		down_dists = [float('inf')]
		left_dists = [float('inf')]
		right_dists = [float('inf')]
		
		dl_dists = [float('inf')]
		dr_dists = [float('inf')]

		for x,y in [(x,y) for x in range(grid_x-3,grid_x+4) for y in range(grid_y-3,grid_y+4)]:
			if not (0 <= x < len(game.solids_map)) or not (0 <= y < len(game.solids_map[0])):
				continue
			if game.solids_map[x][y] == 0:
				continue
			test_rect = pygame.Rect((x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

			#Raycast upward
			up_dists.append(check_ray_rect_collision((self.rect.left+offset, self.rect.top, 0, -1), test_rect))
			up_dists.append(check_ray_rect_collision((self.rect.centerx, self.rect.top, 0, -1), test_rect))
			up_dists.append(check_ray_rect_collision((self.rect.right-offset, self.rect.top, 0, -1), test_rect))

			#Raycast downward
			down_dists.append(check_ray_rect_collision((self.rect.left+offset, self.rect.bottom, 0, 1), test_rect))
			down_dists.append(check_ray_rect_collision((self.rect.centerx, self.rect.bottom, 0, 1), test_rect))
			down_dists.append(check_ray_rect_collision((self.rect.right-offset, self.rect.bottom, 0, 1), test_rect))

			#Raycast left
			left_dists.append(check_ray_rect_collision((self.rect.left, self.rect.top, -1, 0), test_rect))
			left_dists.append(check_ray_rect_collision((self.rect.left, self.rect.centery, -1, 0), test_rect))
			left_dists.append(check_ray_rect_collision((self.rect.left, self.rect.bottom-offset, -1, 0), test_rect))

			#Raycast right
			right_dists.append(check_ray_rect_collision((self.rect.right, self.rect.top, 1, 0), test_rect))
			right_dists.append(check_ray_rect_collision((self.rect.right, self.rect.centery, 1, 0), test_rect))
			right_dists.append(check_ray_rect_collision((self.rect.right, self.rect.bottom-offset, 1, 0), test_rect))

			#Raycast down-left
			dl_dists.append(check_ray_rect_collision((self.rect.left, self.rect.bottom, -1, 1), test_rect))

			#Raycast down-right
			dr_dists.append(check_ray_rect_collision((self.rect.right, self.rect.bottom, 1, 1), test_rect))

		self.col_distances = (min(left_dists) - offset, min(right_dists) - offset, min(up_dists) - offset, min(down_dists) - offset, min(dl_dists), min(dr_dists))


	def set_on_ground(self):
		if self.col_distances[3] < 5:
			self.on_ground = 5

		self.on_ground -= 1
			
Block_Dict = {}

class Block:
	def __init__(self, id, tex, is_solid):
		self.id = id	
		self.texture = tex
		self.is_solid = is_solid

class Blocks:
	def add_block(id, tex, is_solid):
		b = Block(id, tex, is_solid)
		Block_Dict[id] = b
		return b

	Spawn = add_block((0xff,0x00,0x00), None, False)
	Flag = add_block((0xff,0x50,0x00), None, False)
	Coin = add_block((0xff,0xff,0x00), None, False)
	Crab = add_block((0xff,0x80,0x80), None, False)

	Dirt = add_block((0xff,0x88,0x00), tex_dirt, True)
	Grass = add_block((0x00,0xff,0x00), tex_grass, True)
	Brick = add_block((0x88,0x88,0x88), tex_brick, True)
	Stone = add_block((0x20,0x20,0x20), tex_stone, True)
	Cobble = add_block((0x10,0x10,0x10), tex_cobble, True)

class Button(pygame.sprite.Sprite):
	def __init__(self, x, y, level_name):
		super().__init__()
		self.level_name = level_name

		button_size = (500, 80)

		if os.path.exists(os.path.join(path, "data", "platformer", "thumbnails", level_name)):
			img = pygame.image.load(os.path.join(path, "data", "platformer", "thumbnails", level_name))
			button_size = (80 / img.get_height() * img.get_width(), 80) 	
			img = pygame.transform.scale(img, button_size)
			self.texture = img
		else:
			self.texture = pygame.Surface(button_size)
			self.texture.fill((128,128,128))
		
		self.rect = Rect(x, y, *button_size)

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

		self.solids_map = [[0]*img.size[1] for i in range(img.size[0])]

		for x,y in [(x,y) for x in range(img.size[0]) for y in range(img.size[1])]:
			pixel = img.getpixel((x,y))[0:3] #Ignore pixel alpha channel

			if pixel != (0,0,0):
				if pixel in Block_Dict and Block_Dict[pixel].is_solid:
					self.solids_map[x][y] = 1
				
				if pixel == Blocks.Spawn.id:
					START_POS = vec(x * BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE - 2)
				elif pixel == Blocks.Flag.id:
					flag = Flag(x * BLOCK_SIZE, y * BLOCK_SIZE)
					self.entities.add(flag)
				elif pixel == Blocks.Coin.id:
					coin = Coin(x * BLOCK_SIZE, y * BLOCK_SIZE)
					self.entities.add(coin)
				elif pixel == Blocks.Crab.id:
					crab = Crab(x * BLOCK_SIZE, y * BLOCK_SIZE)
					self.entities.add(crab)
				elif pixel == Blocks.Dirt.id:
					dirt_textures = [tex_dirt_l, tex_dirt_r, tex_dirt]

					left = None
					try:
						left = img.getpixel((x-1,y))[0:3]
					except:
						pass
					if left in Block_Dict and (Block_Dict[left] == Blocks.Dirt or Block_Dict[left] == Blocks.Grass):
						dirt_textures.remove(tex_dirt_l)

					right = None	
					try:
						right = img.getpixel((x+1,y))[0:3]
					except:
						pass
					if right in Block_Dict and (Block_Dict[right] == Blocks.Dirt or Block_Dict[right] == Blocks.Grass):
						dirt_textures.remove(tex_dirt_r)

					plat = Platform(x * BLOCK_SIZE, y * BLOCK_SIZE, dirt_textures[0])
					self.platforms.add(plat)
				elif pixel == Blocks.Grass.id:
					#Grass L, Grass M, Grass R
					grass_textures = [tex_grass_l, tex_grass_r, tex_grass]

					left = None	
					try:
						left = img.getpixel((x-1,y))[0:3]
					except:
						pass
					if left in Block_Dict and Block_Dict[left].is_solid:
						grass_textures.remove(tex_grass_l)

					right = None
					try:	
						right = img.getpixel((x+1,y))[0:3]
					except:
						pass
					if right in Block_Dict and Block_Dict[right].is_solid:
						grass_textures.remove(tex_grass_r)

					plat = Platform(x * BLOCK_SIZE, y * BLOCK_SIZE, grass_textures[0])
					self.platforms.add(plat)
				elif pixel == Blocks.Cobble.id:
					cobble_textures = [tex_cobble_l, tex_cobble_r, tex_cobble]
					
					left = None	
					try:
						left = img.getpixel((x-1,y))[0:3]
					except:
						pass
					if left in Block_Dict and Block_Dict[left].is_solid:
						cobble_textures.remove(tex_cobble_l)
				
					right = None
					try:	
						right = img.getpixel((x+1,y))[0:3]
					except:
						pass
					if right in Block_Dict and Block_Dict[right].is_solid:
						cobble_textures.remove(tex_cobble_r)

					plat = Platform(x * BLOCK_SIZE, y * BLOCK_SIZE, cobble_textures[0])
					self.platforms.add(plat)
				else:
					if pixel in Block_Dict:
						plat = Platform(x * BLOCK_SIZE, y * BLOCK_SIZE, Block_Dict[pixel].texture)
					else:
						plat = Platform(x * BLOCK_SIZE, y * BLOCK_SIZE, tex_dirt)
					self.platforms.add(plat)

		self.player = Player(START_POS)
		self.entities.add(self.player)

		self.game_map = pygame.Surface((img.size[0] * BLOCK_SIZE, img.size[1] * BLOCK_SIZE))
		self.game_map.set_colorkey((255,0,255))
		self.background = pygame.Surface((img.size[0] * BLOCK_SIZE, img.size[1] * BLOCK_SIZE))
		self.background.set_colorkey((255,0,255))
		self.background.fill((100,100,220))

		for plat in self.platforms:
			self.background.blit(plat.texture, plat.rect)
		

		if not os.path.exists(os.path.join(path, "data", "platformer", "thumbnails")):
			os.makedirs(os.path.join(path, "data", "platformer", "thumbnails"))
		pygame.image.save(self.background, os.path.join(path, "data", "platformer", "thumbnails", level_name))

		self.window_pos = [0,0]
		self.score = 0

	def main_loop(self):
		last_frame = last_anim = time.perf_counter()
		current_level = 0
		state = 0
		frame_count = 0
		running = True

		self.load_level(self.map_names[current_level])

		self.gui = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.gui.set_colorkey((255,0,255))

		self.scroll_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), flags=SRCALPHA)
		self.scroll_surf.set_colorkey((255,0,255))

		start_buttons = []
		for i, name in enumerate(self.map_names):
			button = Button(0, SCREEN_HEIGHT / 3 + i * 100, name)
			start_buttons.append(button)

		while running:
			current_time = time.perf_counter()

			if (current_time - last_frame) > 1.0 / 57 and state != 0:
				print("Stuttering")


			mouse_pos = pygame.mouse.get_pos()

			# Update Game
			if state == 0:
				for event in pygame.event.get():
					if event.type == QUIT:
						running = False
					elif event.type == MOUSEBUTTONDOWN and event.button == 1:
						for i, button in enumerate(start_buttons):
							if button.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
								self.load_level(self.map_names[i])
								current_level = i
								state = 1
					elif event.type == MOUSEWHEEL:
						for button in start_buttons:
							button.rect.centery += 10 * event.y
					elif event.type == KEYDOWN:
						if event.key == K_SPACE:
							self.load_level(self.map_names[current_level])
							state = 1
			else:
				for event in pygame.event.get():
					if event.type == QUIT:
						running = False
					elif event.type == KEYDOWN:
						if event.key == K_SPACE:
							self.player.jump()

				for entity in self.entities:
					entity.update(self)

				if self.player.pos.y > SCREEN_HEIGHT + PLAYER_HEIGHT + 1:
					state = 0
			
			#Update Animations
			if current_time - last_anim > 1.0 / ANIM_RATE:
				for entity in self.entities:
					entity.update_anims(self)
				last_anim = current_time

			# Rendering Code
			# Move window along with player
			if self.player.pos.x > (-self.window_pos[0] + SCREEN_WIDTH * 0.7):
				self.window_pos[0] -= abs(self.player.vel.x)
			if self.player.pos.x < (-self.window_pos[0] + SCREEN_WIDTH * 0.2) and self.player.pos.x > SCREEN_WIDTH * 0.2:
				self.window_pos[0] += abs(self.player.vel.x)

			# Create game map surface	
			self.gui.fill((255,0,255,0))
			score_text = font.render('Score: ' + str(self.score), False, (255,255,255))
			pygame.Surface.blit(self.gui,score_text, (1 * BLOCK_SIZE, 1 * BLOCK_SIZE))

			self.game_map.fill((100,100,220))
			self.game_map.blit(self.background, (0,0))
	
			for entity in self.entities:
				self.game_map.blit(entity.texture, entity.rect)

			# Blit Game Map, GUI, and Main menu onto the screen
			window.fill((0,0,0))
			window.blit(self.game_map, self.window_pos)
			window.blit(self.gui, (0,0))

			if state == 0:
				self.scroll_surf.fill((40,40,40, 100))
				self.scroll_surf.convert_alpha()
				# Blit menu GUI
				for button in start_buttons:
					self.scroll_surf.blit(button.texture, button.rect)
					#pygame.Surface.fill(self.scroll_surf, (128,128,128), button.rect)

				window.blit(self.scroll_surf, (0,0))

			pygame.display.update()

			last_frame = current_time
			frame_count += 1
			clock.tick(60)

		pygame.display.quit()
		pygame.quit()
		sys.exit()

if __name__ == '__main__':
	game = Game()