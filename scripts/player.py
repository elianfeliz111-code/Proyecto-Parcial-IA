# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

import pygame
import os
from scripts.settings import *

class Player:

    #---inicialización del jugador---
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.velocidad = JUGADOR_VELOCIDAD

        #---animaciones---
        self.animaciones = {}
        self.cargar_animaciones()

        self.estado = "Idle"
        self.direccion = "Down"
        self.voltear = False
        self.frame = 0
        self.vel_anim = JUGADOR_VEL_ANIM

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

        #---sonidos---
        self.sonido_caminar = pygame.mixer.Sound(RUTA_SONIDO_PASOS)
        self.sonido_caminar.set_volume(0.4)
        self.caminando = False

        #---vida---
        self.vidas = JUGADOR_VIDAS
        self.vidas_max = JUGADOR_VIDAS
        self.vivo = True

        #---invencibilidad temporal al recibir daño---
        self.invencible = False
        self.tiempo_invencible = JUGADOR_TIEMPO_INVENCIBLE
        self.timer_invencible = 0.0
        self.visible = True

        #---ataque---
        self.atacando = False
        self.frame_ataque = 0
        self.vel_anim_ataque = JUGADOR_VEL_ANIM_ATAQUE
        self.ataque_hitbox = None
        self.ataque_danio = 1
        self.ataque_aplicado = False

    #---carga todas las animaciones del jugador---
    def cargar_animaciones(self):
        base = "assets/animation/player"
        estados = ["Idle", "Run", "Attack"]
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

    #---input del jugador---
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

            #---iniciar ataque con Space o J---
            elif event.key in (pygame.K_SPACE, pygame.K_j):
                if not self.atacando:
                    self.atacando = True
                    self.frame_ataque = 0
                    self.ataque_aplicado = False

        elif event.type == pygame.KEYUP:

            if event.key == pygame.K_a and "LEFT" in self.teclas:
                self.teclas.remove("LEFT")

            elif event.key == pygame.K_d and "RIGHT" in self.teclas:
                self.teclas.remove("RIGHT")

            elif event.key == pygame.K_w and "UP" in self.teclas:
                self.teclas.remove("UP")

            elif event.key == pygame.K_s and "DOWN" in self.teclas:
                self.teclas.remove("DOWN")

    #---movimiento con colisiones---
    def mover(self, dt, colisiones):

        #---no se mueve mientras ataca---
        if self.atacando:
            self.estado = "Attack"
            return

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
            if not self.caminando:
                self.sonido_caminar.play(-1)
                self.caminando = True

        if not moviendo:
            self.estado = "Idle"
            if self.caminando:
                self.sonido_caminar.stop()
                self.caminando = False

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

    #---animacion general---
    def animar(self, dt):

        if self.atacando:
            self.animar_ataque(dt)
            return

        frames = self.animaciones[self.estado][self.direccion]

        self.frame += self.vel_anim * dt

        if self.frame >= len(frames):
            self.frame = 0

        self.image = frames[int(self.frame)]

    #---animacion de ataque---
    def animar_ataque(self, dt):
        frames = self.animaciones["Attack"][self.direccion]
        self.frame_ataque += self.vel_anim_ataque * dt

        if self.frame_ataque >= len(frames):

            #---termina el ataque---
            self.atacando = False
            self.ataque_hitbox = None
            self.frame_ataque = 0
            self.estado = "Idle"
            self.image = self.animaciones["Idle"][self.direccion][0]
            return

        self.image = frames[int(self.frame_ataque)]
        self.actualizar_hitbox_ataque()

    #---calcula la hitbox del ataque segun la direccion---
    def actualizar_hitbox_ataque(self):
        size = (24, 16)

        if self.direccion == "Down":
            self.ataque_hitbox = pygame.Rect(
                self.hitbox.centerx - size[0] // 2,
                self.hitbox.bottom,
                size[0], size[1]
            )
        elif self.direccion == "Up":
            self.ataque_hitbox = pygame.Rect(
                self.hitbox.centerx - size[0] // 2,
                self.hitbox.top - size[1],
                size[0], size[1]
            )
        elif self.direccion == "Side":
            if self.voltear:
                self.ataque_hitbox = pygame.Rect(
                    self.hitbox.left - size[1],
                    self.hitbox.centery - size[0] // 2,
                    size[1], size[0]
                )
            else:
                self.ataque_hitbox = pygame.Rect(
                    self.hitbox.right,
                    self.hitbox.centery - size[0] // 2,
                    size[1], size[0]
                )

    #---recibir daño (llamado por el enemigo)---
    def recibir_danio(self, cantidad=1):
        if self.invencible or not self.vivo:
            return

        self.vidas -= cantidad
        self.invencible = True
        self.timer_invencible = 0.0

        if self.vidas <= 0:
            self.vidas = 0
            self.vivo = False

    #---actualiza invencibilidad y parpadeo---
    def actualizar_invencibilidad(self, dt):
        if not self.invencible:
            self.visible = True
            return

        self.timer_invencible += dt

        #---parpadeo cada 0.1 segundos---
        self.visible = int(self.timer_invencible * 10) % 2 == 0

        if self.timer_invencible >= self.tiempo_invencible:
            self.invencible = False
            self.visible = True

    #---update principal---
    def update(self, dt, colisiones):
        if not self.vivo:
            return

        self.mover(dt, colisiones)
        self.animar(dt)
        self.actualizar_invencibilidad(dt)