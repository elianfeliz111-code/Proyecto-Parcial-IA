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

        self.teclas = []


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
                        img = pygame.image.load(
                            os.path.join(ruta, archivo)
                        ).convert_alpha()
                        frames.append(img)

                    self.animaciones[estado][dir] = frames

    def input(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_a and "LEFT" not in self.teclas:
                self.teclas.append("LEFT")

            elif event.key == pygame.K_d and "RIGHT" not in self.teclas:
                self.teclas.append("RIGHT")

            elif event.key == pygame.K_w and "UP" not in self.teclas:
                self.teclas.append("UP")

            elif event.key == pygame.K_s and "DOWN" not in self.teclas:
                self.teclas.append("DOWN")


        elif event.type == pygame.KEYUP:

            if event.key == pygame.K_a and "LEFT" in self.teclas:
                self.teclas.remove("LEFT")

            elif event.key == pygame.K_d and "RIGHT" in self.teclas:
                self.teclas.remove("RIGHT")

            elif event.key == pygame.K_w and "UP" in self.teclas:
                self.teclas.remove("UP")

            elif event.key == pygame.K_s and "DOWN" in self.teclas:
                self.teclas.remove("DOWN")


    def mover(self, dt):

        moviendo = False

        if self.teclas:

            direccion = self.teclas[-1]

            if direccion == "LEFT":
                self.pos.x -= self.velocidad * dt
                self.direccion = "Side"
                self.voltear = True

            elif direccion == "RIGHT":
                self.pos.x += self.velocidad * dt
                self.direccion = "Side"
                self.voltear = False

            elif direccion == "UP":
                self.pos.y -= self.velocidad * dt
                self.direccion = "Up"

            elif direccion == "DOWN":
                self.pos.y += self.velocidad * dt
                self.direccion = "Down"

            self.estado = "Run"
            moviendo = True

        if not moviendo:
            self.estado = "Idle"

        self.rect.topleft = self.pos


    def animar(self, dt):

        frames = self.animaciones[self.estado][self.direccion]

        self.frame += self.vel_anim * dt

        if self.frame >= len(frames):
            self.frame = 0

        self.image = frames[int(self.frame)]


    def update(self, dt):
        self.mover(dt)
        self.animar(dt)


    def draw(self, surface):
        imagen = self.image

        if self.voltear:
            imagen = pygame.transform.flip(self.image, True, False)

        surface.blit(imagen, self.rect)