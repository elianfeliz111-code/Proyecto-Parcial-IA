# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

import pygame
import os
import random
from scripts.behaviour_tree import Secuencia, Selector, Accion, Condicion, SUCCESS, FAILURE, RUNNING
from scripts.astar import astar

class Skeleton:

    def __init__(self, x, y, tile_w, tile_h, colisiones):
        self.pos = pygame.Vector2(x, y)
        self.velocidad = 150
        self.tile_w = tile_w
        self.tile_h = tile_h

        self._colisiones_rects = colisiones

        # ---colisiones en formato set de tiles para el A*---
        self.colisiones_set = set()
        for rect in colisiones:
            # ---marca todos los tiles que toca el rect, no solo el origen---
            tx_inicio = rect.x // tile_w
            ty_inicio = rect.y // tile_h
            tx_fin = (rect.x + rect.width - 1) // tile_w
            ty_fin = (rect.y + rect.height - 1) // tile_h
            for tx in range(tx_inicio, tx_fin + 1):
                for ty in range(ty_inicio, ty_fin + 1):
                    self.colisiones_set.add((tx, ty))

        # ---animaciones---
        self.animaciones = {}
        self.cargar_animaciones()

        # ---corazon para la vida---
        corazon_original = pygame.image.load("assets/images/heart.png").convert_alpha()
        self.corazon = pygame.transform.scale(corazon_original, (12, 12))

        self.estado = "Idle"
        self.direccion = "Down"
        self.voltear = False
        self.frame = 0
        self.vel_anim = 6

        self.image = self.animaciones["Idle"]["Down"][0]
        self.rect = self.image.get_rect(topleft=self.pos)
        self.hitbox = pygame.Rect(self.rect.x + 8, self.rect.y + 24, 16, 24)

        # ---vida---
        self.vidas = 3
        self.vivo = True

        # ---muerte---
        self.muriendo = False
        self.frame_muerte = 0
        self.vel_anim_muerte = 6
        self.muerto_completado = False

        # ---invencibilidad temporal---
        self.invencible = False
        self.timer_invencible = 0.0
        self.tiempo_invencible = 0.5
        self.visible = True

        # ---ataque melee---
        self.atacando = False
        self.frame_ataque = 0
        self.vel_anim_ataque = 8
        self.cooldown_ataque = 1.5
        self.timer_ataque = 0.0
        self.rango_ataque = 28
        self.danio = 1
        self._danio_aplicado = False

        # ---pathfinding A*---
        self.camino = []
        self.timer_camino = 0.0
        self.intervalo_camino = 0.5

        # ---linea de vision---
        self.radio_vision = 180

        # ---patrulla aleatoria---
        self.waypoint_patrulla = None
        self.timer_patrulla = 0.0
        self.intervalo_patrulla = 3.0
        self.radio_patrulla = 5

        # ---delta time guardado para usar en acciones del arbol---
        self._dt = 0

        # ---arbol de comportamiento---
        self.arbol = self.construir_arbol()

        # ---referencia al jugador---
        self.jugador = None

    def cargar_animaciones(self):
        base = "assets/animation/skeleton"
        estados_dir = {
            "Idle":   ["Up", "Down", "Side"],
            "Run":    ["Up", "Down", "Side"],
            "Attack": ["Up", "Down", "Side"],
        }

        for estado, dirs in estados_dir.items():
            self.animaciones[estado] = {}
            for d in dirs:
                ruta = os.path.join(base, estado, d)
                if os.path.exists(ruta):
                    frames = []
                    for archivo in sorted(os.listdir(ruta)):
                        img = pygame.image.load(os.path.join(ruta, archivo)).convert_alpha()
                        frames.append(img)
                    self.animaciones[estado][d] = frames

        # ---animacion de muerte (sin subdirecciones)---
        ruta_death = os.path.join(base, "Death")
        if os.path.exists(ruta_death):
            frames = []
            for archivo in sorted(os.listdir(ruta_death)):
                img = pygame.image.load(os.path.join(ruta_death, archivo)).convert_alpha()
                frames.append(img)
            self.animaciones["Death"] = frames

    # ---construye el arbol de comportamiento---
    def construir_arbol(self):
        return Selector([
            Secuencia([
                Condicion(self.puede_atacar),
                Accion(self.hacer_ataque),
            ]),
            Secuencia([
                Condicion(self.tiene_linea_de_vision),
                Accion(self.perseguir),
            ]),
            Accion(self.patrullar),
        ])

    # ---condicion: jugador en rango de ataque y cooldown listo---
    def puede_atacar(self):
        if self.jugador is None or self.atacando:
            return False
        if self.timer_ataque > 0:
            return False
        distancia = self.pos.distance_to(self.jugador.pos)
        return distancia <= self.rango_ataque

    # ---condicion: hay linea de vision hasta el jugador---
    def tiene_linea_de_vision(self):
        if self.jugador is None:
            return False
        distancia = self.pos.distance_to(self.jugador.pos)
        if distancia > self.radio_vision:
            return False
        return self.comprobar_linea_de_vision()

    # ---raycast en pixeles para verificar que no hay pared entre el esqueleto y el jugador---
    def comprobar_linea_de_vision(self):
        x0 = self.hitbox.centerx
        y0 = self.hitbox.centery
        x1 = self.jugador.hitbox.centerx
        y1 = self.jugador.hitbox.centery

        dx = x1 - x0
        dy = y1 - y0
        distancia = max(abs(dx), abs(dy))

        if distancia == 0:
            return True

        pasos = int(distancia // 8)
        if pasos == 0:
            return True

        paso_x = dx / pasos
        paso_y = dy / pasos

        for i in range(pasos):
            px = x0 + paso_x * i
            py = y0 + paso_y * i
            for rect in self._colisiones_rects:
                if rect.collidepoint(px, py):
                    return False

        return True

    # ---accion: iniciar animacion de ataque---
    def hacer_ataque(self):
        if not self.atacando:
            self.atacando = True
            self.frame_ataque = 0
            self._danio_aplicado = False
        return RUNNING

    # ---accion: moverse hacia el jugador siguiendo el camino A*---
    def perseguir(self):
        if self.jugador is None:
            return FAILURE

        if self.camino:
            destino = pygame.Vector2(self.camino[0])
            direccion = destino - self.pos

            if direccion.length() < 4:
                self.camino.pop(0)
            else:
                direccion = direccion.normalize()
                movimiento = direccion * self.velocidad * self._dt

                # ---colision en X---
                self.hitbox.x += int(movimiento.x)
                for rect in self._colisiones_rects:
                    if self.hitbox.colliderect(rect):
                        if movimiento.x > 0:
                            self.hitbox.right = rect.left
                        elif movimiento.x < 0:
                            self.hitbox.left = rect.right

                # ---colision en Y---
                self.hitbox.y += int(movimiento.y)
                for rect in self._colisiones_rects:
                    if self.hitbox.colliderect(rect):
                        if movimiento.y > 0:
                            self.hitbox.bottom = rect.top
                        elif movimiento.y < 0:
                            self.hitbox.top = rect.bottom

                self.rect.midbottom = self.hitbox.midbottom
                self.pos = pygame.Vector2(self.rect.topleft)

                if abs(direccion.x) > abs(direccion.y):
                    self.direccion = "Side"
                    self.voltear = direccion.x < 0
                elif direccion.y < 0:
                    self.direccion = "Up"
                else:
                    self.direccion = "Down"

                self.estado = "Run"

        return RUNNING

    #---accion: patrullar a tiles aleatorios cercanos---
    def patrullar(self):
        if self.waypoint_patrulla is None:
            self.elegir_waypoint_patrulla()
            return RUNNING

        if self.camino:
            destino = pygame.Vector2(self.camino[0])
            direccion = destino - self.pos

            if direccion.length() < 4:
                self.camino.pop(0)
            else:
                direccion = direccion.normalize()
                movimiento = direccion * (self.velocidad * 0.75) * self._dt

                #---colision en X---
                self.hitbox.x += int(movimiento.x)
                for rect in self._colisiones_rects:
                    if self.hitbox.colliderect(rect):
                        if movimiento.x > 0:
                            self.hitbox.right = rect.left
                        elif movimiento.x < 0:
                            self.hitbox.left = rect.right

                #---colision en Y---
                self.hitbox.y += int(movimiento.y)
                for rect in self._colisiones_rects:
                    if self.hitbox.colliderect(rect):
                        if movimiento.y > 0:
                            self.hitbox.bottom = rect.top
                        elif movimiento.y < 0:
                            self.hitbox.top = rect.bottom

                self.rect.midbottom = self.hitbox.midbottom
                self.pos = pygame.Vector2(self.rect.topleft)

                if abs(direccion.x) > abs(direccion.y):
                    self.direccion = "Side"
                    self.voltear = direccion.x < 0
                elif direccion.y < 0:
                    self.direccion = "Up"
                else:
                    self.direccion = "Down"

                self.estado = "Run"

        else:
            #---llego al destino, elegir otro---
            self.waypoint_patrulla = None
            self.estado = "Idle"

        return RUNNING

    #---elige un tile libre aleatorio cercano como destino de patrulla---
    def elegir_waypoint_patrulla(self):
        tx_actual = int(self.pos.x // self.tile_w)
        ty_actual = int(self.pos.y // self.tile_h)

        intentos = 0
        while intentos < 20:
            dx = random.randint(-self.radio_patrulla, self.radio_patrulla)
            dy = random.randint(-self.radio_patrulla, self.radio_patrulla)
            tx = tx_actual + dx
            ty = ty_actual + dy

            if (tx, ty) not in self.colisiones_set:
                self.waypoint_patrulla = (
                    tx * self.tile_w + self.tile_w // 2,
                    ty * self.tile_h + self.tile_h // 2
                )
                return
            intentos += 1

        self.waypoint_patrulla = None

    # ---recalcular camino A* periodicamente---
    def actualizar_camino(self, dt):
        self.timer_camino += dt
        if self.timer_camino >= self.intervalo_camino:
            self.timer_camino = 0

            if self.jugador and self.tiene_linea_de_vision():
                # ---perseguir al jugador---
                self.camino = astar(
                    (self.pos.x, self.pos.y),
                    (self.jugador.pos.x, self.jugador.pos.y),
                    self.colisiones_set,
                    self.tile_w,
                    self.tile_h
                )
            elif self.waypoint_patrulla:
                # ---camino hacia el waypoint de patrulla---
                self.camino = astar(
                    (self.pos.x, self.pos.y),
                    self.waypoint_patrulla,
                    self.colisiones_set,
                    self.tile_w,
                    self.tile_h
                )

    # ---animacion segun estado actual---
    def animar(self, dt):
        if self.muriendo:
            frames = self.animaciones["Death"]
            self.frame_muerte += self.vel_anim_muerte * dt
            if self.frame_muerte >= len(frames):
                self.frame_muerte = len(frames) - 1
                self.muerto_completado = True
            self.image = frames[int(self.frame_muerte)]
            return

        if self.atacando:
            frames = self.animaciones["Attack"][self.direccion]
            self.frame_ataque += self.vel_anim_ataque * dt

            # ---aplica daño en el frame 2 del ataque---
            if int(self.frame_ataque) >= 2 and not self._danio_aplicado:
                if self.jugador:
                    distancia = self.pos.distance_to(self.jugador.pos)
                    if distancia <= self.rango_ataque:
                        self.jugador.recibir_danio(self.danio)
                self._danio_aplicado = True

            if self.frame_ataque >= len(frames):
                self.atacando = False
                self.frame_ataque = 0
                self.timer_ataque = self.cooldown_ataque
                self._danio_aplicado = False
                self.estado = "Idle"
                return

            self.image = frames[int(self.frame_ataque)]
            return

        if self.estado == "Run":
            frames = self.animaciones["Run"][self.direccion]
        else:
            frames = self.animaciones["Idle"][self.direccion]

        self.frame += self.vel_anim * dt
        if self.frame >= len(frames):
            self.frame = 0

        self.image = frames[int(self.frame)]

    # ---recibir daño del jugador---
    def recibir_danio(self, cantidad=1):
        if self.invencible or not self.vivo:
            return
        self.vidas -= cantidad
        self.invencible = True
        self.timer_invencible = 0.0
        if self.vidas <= 0:
            self.vidas = 0
            self.vivo = False
            self.muriendo = True

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

    def update(self, dt, jugador):
        if self.muerto_completado:
            return

        self._dt = dt
        self.jugador = jugador

        if self.muriendo:
            self.animar(dt)
            return

        if self.timer_ataque > 0:
            self.timer_ataque -= dt

        #---si no ve al jugador, contar tiempo para nueva patrulla---
        if not self.tiene_linea_de_vision():
            self.timer_patrulla += dt
            if self.timer_patrulla >= self.intervalo_patrulla:
                self.waypoint_patrulla = None
                self.timer_patrulla = 0.0

        self.actualizar_camino(dt)
        self.arbol.ejecutar()
        self.animar(dt)
        self.actualizar_invencibilidad(dt)

    def draw(self, surface, cam_x, cam_y):
        if self.muerto_completado:
            return

        if not self.visible:
            return

        imagen = self.image
        if self.voltear:
            imagen = pygame.transform.flip(self.image, True, False)

        surface.blit(imagen, (self.rect.x - cam_x, self.rect.y - cam_y))

        #---corazones de vida sobre el esqueleto---
        if self.vivo:
            for i in range(self.vidas):
                x = self.rect.x - cam_x + i * 11
                y = self.rect.y - cam_y - 10
                surface.blit(self.corazon, (x, y))