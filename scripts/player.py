# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

import pygame

class Player:
#inicialización del jugador
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.velocidad = 300

#actualización del jugador
    def update(self, dt):
        self.mover(dt)

#movimiento del jugador
    def mover(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rect.x -= self.velocidad * dt
        if keys[pygame.K_d]:
            self.rect.x += self.velocidad * dt
        if keys[pygame.K_w]:
            self.rect.y -= self.velocidad * dt
        if keys[pygame.K_s]:
            self.rect.y += self.velocidad * dt

#dibujado del jugador
    def draw(self, surface):
        pygame.draw.rect(surface, (200, 0, 0), self.rect)