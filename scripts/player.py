# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

import pygame
import os

class Player:

    #---inicialización del jugador---
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.velocidad = 100

    #---animaciones---
        self.animaciones = {}
        self.cargar_animaciones()

        self.estado = "Idle"
        self.direccion = "Down"
        self.voltear = False
        self.frame = 0
        self.vel_anim = 5

        self.image = self.animaciones[self.estado][self.direccion][0]
        self.rect = self.image.get_rect(topleft=self.pos)

        #---hitbox del jugador---
        self.hitbox = pygame.Rect(
            self.rect.x + 8,
            self.rect.y + 24,
            16,
            24
        )

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


    def mover(self, dt, colisiones):

        moviendo = False
        movimiento = pygame.Vector2(0, 0)

        if self.teclas:

            direccion = self.teclas[-1]

            if direccion == "LEFT":
                movimiento.x = -self.velocidad * dt
                self.direccion = "Side"
                self.voltear = True

            elif direccion == "RIGHT":
                movimiento.x = self.velocidad * dt
                self.direccion = "Side"
                self.voltear = False

            elif direccion == "UP":
                movimiento.y = -self.velocidad * dt
                self.direccion = "Up"

            elif direccion == "DOWN":
                movimiento.y = self.velocidad * dt
                self.direccion = "Down"

            self.estado = "Run"
            moviendo = True

        if not moviendo:
            self.estado = "Idle"

        self.hitbox.x += movimiento.x

        for rect in colisiones:
            if self.hitbox.colliderect(rect):
                if movimiento.x > 0:
                    self.hitbox.right = rect.left
                elif movimiento.x < 0:
                    self.hitbox.left = rect.right

        self.hitbox.y += movimiento.y

        for rect in colisiones:
            if self.hitbox.colliderect(rect):
                if movimiento.y > 0:
                    self.hitbox.bottom = rect.top
                elif movimiento.y < 0:
                    self.hitbox.top = rect.bottom

        self.rect.midbottom = self.hitbox.midbottom
        self.pos = pygame.Vector2(self.rect.topleft)


    def animar(self, dt):

        frames = self.animaciones[self.estado][self.direccion]

        self.frame += self.vel_anim * dt

        if self.frame >= len(frames):
            self.frame = 0

        self.image = frames[int(self.frame)]


    def update(self, dt, colisiones):
        self.mover(dt, colisiones)
        self.animar(dt)


    def draw(self, surface):
        imagen = self.image

        if self.voltear:
            imagen = pygame.transform.flip(self.image, True, False)

        surface.blit(imagen, self.rect)

        #pygame.draw.rect(surface, (255,0,0), self.hitbox, 2)