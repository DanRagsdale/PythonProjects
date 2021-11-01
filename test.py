import pygame
import random

from pygame.locals import (
	K_UP,
	K_DOWN,
	K_LEFT,
	K_RIGHT,
	K_ESCAPE,
	KEYDOWN,
	QUIT
)


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

PLAYER_SPEED = 10

class Player(pygame.sprite.Sprite):
	def __init__(self):
		super(Player, self).__init__()
		self.surf = pygame.Surface((75,25))
		self.surf.fill((255,255,255))
		self.rect = self.surf.get_rect()

	def update(self, pressed_keys):
		if pressed_keys[K_UP]:
			self.rect.move_ip(0, -PLAYER_SPEED)
		if pressed_keys[K_DOWN]:
			self.rect.move_ip(0,  PLAYER_SPEED)
		if pressed_keys[K_LEFT]:
			self.rect.move_ip(-PLAYER_SPEED, 0)
		if pressed_keys[K_RIGHT]:
			self.rect.move_ip(PLAYER_SPEED, 0)

		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.right > SCREEN_WIDTH:
			self.rect.right = SCREEN_WIDTH
		if self.rect.top < 0:
			self.rect.top = 0
		if self.rect.bottom > SCREEN_HEIGHT:
			self.rect.bottom = SCREEN_HEIGHT

class Enemy(pygame.sprite.Sprite):
	def __init__(self):
		super(Enemy, self).__init__()
		self.surf = pygame.Surface((20, 10))
		self.surf.fill((255, 128, 128))
		self.rect = self.surf.get_rect(
			center=(
				random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
				random.randint(0, SCREEN_HEIGHT),
			)
		)
		self.speed = random.randint(5, 20)

	def update(self):
		self.rect.move_ip(-self.speed, 0)
		
		if self.rect.right < 0:
			self.kill()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.init()

ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)

player = Player()

enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Begin game code

clock = pygame.time.Clock()

running = True
alive = True
while alive:
	# Event Handler
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				running = False
				alive = False
		elif event.type == QUIT:
			running = False
			alive = False
		elif event.type == ADDENEMY:
			new_enemy = Enemy()
			enemies.add(new_enemy)
			all_sprites.add(new_enemy)

	pressed_keys = pygame.key.get_pressed()

	if running:
		player.update(pressed_keys)
		enemies.update()

		# Game Code
		screen.fill((0,0,0))

		for entity in all_sprites:
			screen.blit(entity.surf, entity.rect)

		if pygame.sprite.spritecollideany(player, enemies):
			running = False

	pygame.display.flip()
	clock.tick(30)

pygame.quit()















