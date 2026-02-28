# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

import pygame
import os

class Player:

#inicialización del jugador
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.velocidad = 150

        # animaciones
        self.animaciones = {}
        self.cargar_animaciones()

        self.estado = "Idle"
        self.direccion = "Down"
        self.voltear = False
        self.frame = 0
        self.vel_anim = 5

        self.image = self.animaciones[self.estado][self.direccion][0]
        self.rect = self.image.get_rect(topleft=self.pos)

#cargar animaciones desde carpetas
    def cargar_animaciones(self):
        base = "assets/animation/player"
        estados = ["Idle", "Run"]
        direcciones = ["Up", "Down", "Side"]

        for estado in estados:
            self.animaciones[estado] = {}

            for dir in direcciones:
                ruta = os.path.join(base, estado, dir)

                if os.path.exists(ruta):
                    frames = []
                    for archivo in sorted(os.listdir(ruta)):
                        img = pygame.image.load(os.path.join(ruta, archivo)).convert_alpha()
                        frames.append(img)

                    self.animaciones[estado][dir] = frames

#animación
    def animar(self, dt):
        frames = self.animaciones[self.estado][self.direccion]

        self.frame += self.vel_anim * dt
        if self.frame >= len(frames):
            self.frame = 0

        self.image = frames[int(self.frame)]

#movimiento del jugador
    def mover(self, dt):
        keys = pygame.key.get_pressed()

        moviendo = False

        if keys[pygame.K_a]:
            self.pos.x -= self.velocidad * dt
            self.estado = "Run"
            self.direccion = "Side"
            self.voltear = True
            moviendo = True

        if keys[pygame.K_d]:
            self.pos.x += self.velocidad * dt
            self.estado = "Run"
            self.direccion = "Side"
            self.voltear = False
            moviendo = True

        if keys[pygame.K_w]:
            self.pos.y -= self.velocidad * dt
            self.estado = "Run"
            self.direccion = "Up"
            moviendo = True

        if keys[pygame.K_s]:
            self.pos.y += self.velocidad * dt
            self.estado = "Run"
            self.direccion = "Down"
            moviendo = True

        if not moviendo:
            self.estado = "Idle"

        self.rect.topleft = self.pos

#actualización del jugador
    def update(self, dt):
        self.mover(dt)
        self.animar(dt)

#dibujado del jugador
    def draw(self, surface):
        imagen = self.image
        if self.voltear:
            imagen = pygame.transform.flip(self.image, True, False)
        surface.blit(imagen, self.rect)