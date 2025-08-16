import pygame 

#button class
class Button():
	def __init__(self, image):
		self.width = image.get_width()
		self.height = image.get_height()
		self.image = image
		self.clicked = False

	def draw(self, surface, x, y, scale):
		action = False

		self.image = pygame.transform.scale(self.image, (int(self.width * scale), int(self.height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		# pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action