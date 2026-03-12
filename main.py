# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

import pygame,sys
from scripts.player import Player
from scripts.menu import Menu
from scripts.map import Map
from scripts.hud import HUD
from scripts.skeleton import Skeleton
from scripts.settings import *

class Game:
    #---inicializacion---
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        #---sonidos---
        self.sonido_menu = pygame.mixer.Sound(RUTA_SONIDO_MENU)
        self.sonido_perder = pygame.mixer.Sound(RUTA_SONIDO_PERDER)
        self.sonido_esqueleto = pygame.mixer.Sound(RUTA_SONIDO_ESQUELETO)
        self.sonido_menu.play()

        #---musica de fondo---
        self.musica_juego = pygame.mixer.Sound(RUTA_MUSICA)
        self.musica_juego.set_volume(0.5)
        self.musica_iniciada = False

        #---ventana---
        self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.pantalla_completa = True
        pygame.display.set_caption(TITULO)

        self.reloj = pygame.time.Clock()
        self.jugando = True

        #---hud---
        self.hud = HUD()

        #---fuentes---
        self.fuente = pygame.font.Font(RUTA_FUENTE, 40)
        self.fuente_pequeña = pygame.font.Font(RUTA_FUENTE, 24)
        self.fuente_mini = pygame.font.Font(RUTA_FUENTE, 18)

        #---zoom---
        self.zoom = ZOOM

        #---menu---
        self.menu = Menu(self.ventana, RUTA_FONDO_MENU)
        self.estado = "menu"

        self.iniciar_juego()

    #---inicializa o reinicia el estado del juego---
    def iniciar_juego(self):
        #---mapa---
        self.mapa = Map(RUTA_MAPA)

        #---tamaño del tile---
        self.tile_w = self.mapa.tmx.tilewidth
        self.tile_h = self.mapa.tmx.tileheight

        #---spawn del jugador---
        spawn_x = JUGADOR_SPAWN_X * self.tile_w
        spawn_y = JUGADOR_SPAWN_Y * self.tile_h
        self.player = Player(spawn_x, spawn_y)

        #---enemigos---
        self.esqueletos = [
            Skeleton(3 * self.tile_w, 8 * self.tile_h, self.tile_w, self.tile_h, self.mapa.colisiones),
            Skeleton(15 * self.tile_w, 4 * self.tile_h, self.tile_w, self.tile_h, self.mapa.colisiones),
            Skeleton(12 * self.tile_w, 15 * self.tile_h, self.tile_w, self.tile_h, self.mapa.colisiones),
            Skeleton(15 * self.tile_w, 10 * self.tile_h, self.tile_w, self.tile_h, self.mapa.colisiones),
            Skeleton(13 * self.tile_w, 6 * self.tile_h, self.tile_w, self.tile_h, self.mapa.colisiones),
            Skeleton(4 * self.tile_w, 3 * self.tile_h, self.tile_w, self.tile_h, self.mapa.colisiones)
        ]

        #---cámara---
        self.camera_offset = pygame.Vector2(0, 0)
        self.camera_target = pygame.Vector2(0, 0)
        self.camera_smoothness = CAMARA_SMOOTHNESS

        #---contador de esqueletos eliminados---
        self.esqueletos_eliminados = 0

        #---resetear musica---
        self.musica_juego.stop()
        self.musica_iniciada = False

    #---bucle principal del juego---
    def run(self):
        while self.jugando:
            #---delta time---
            dt = self.reloj.tick(FPS) / 1000

            if self.estado == "menu":
                self.estado_menu(dt)

            elif self.estado == "juego":
                self.estado_juego(dt)

            elif self.estado == "game_over":
                self.estado_game_over()

            elif self.estado == "victoria":
                self.estado_victoria()

            self.draw()

        pygame.quit()
        sys.exit()

    #---estado del menu---
    def estado_menu(self, dt):
        resultado = self.menu.update(dt)

        if resultado == "jugar":
            self.iniciar_juego()
            self.estado = "juego"

        elif resultado == "salir":
            self.jugando = False

    #---estado del juego---
    def estado_juego(self, dt):

        #---iniciar musica de fondo cuando empieza el juego---
        if not self.musica_iniciada:
            self.musica_juego.play(-1)
            self.musica_iniciada = True

        self.events()
        self.player.update(dt, self.mapa.colisiones)

        for esqueleto in self.esqueletos:
            esqueleto.update(dt, self.player)

        #---si el jugador ataca y tiene hitbox activa---
        if self.player.atacando and self.player.ataque_hitbox:
            for esqueleto in self.esqueletos:
                if self.player.ataque_hitbox.colliderect(esqueleto.hitbox):
                    if not self.player.ataque_aplicado:
                        esqueleto.recibir_danio(self.player.ataque_danio)
                        self.player.ataque_aplicado = True

        #---detectar esqueletos muertos y reproducir sonido---
        esqueletos_antes = len(self.esqueletos)
        self.esqueletos = [e for e in self.esqueletos if not e.muerto_completado]
        esqueletos_eliminados_ahora = esqueletos_antes - len(self.esqueletos)

        #---sumar al contador si se elimino algun esqueleto---
        if esqueletos_eliminados_ahora > 0:
            self.esqueletos_eliminados += esqueletos_eliminados_ahora
            self.sonido_esqueleto.play()

        #---detecta tile actual del jugador---
        tile_x = int(self.player.rect.x // self.tile_w)
        tile_y = int(self.player.rect.y // self.tile_h)

        #---condicion de victoria: llegar al tile 4,1 Y haber matado al menos 3 esqueletos---
        if tile_x == 4 and tile_y == 0 and self.esqueletos_eliminados >= 3:
            self.musica_juego.stop()
            self.estado = "victoria"

        ancho_visible = self.ventana.get_width() / self.zoom
        alto_visible = self.ventana.get_height() / self.zoom

        self.camera_target.x = self.player.rect.centerx - ancho_visible / 2
        self.camera_target.y = self.player.rect.centery - alto_visible / 2

        #---limite de camara---
        self.camera_target.x = max(0, min(self.camera_target.x, self.mapa.width - ancho_visible))
        self.camera_target.y = max(0, min(self.camera_target.y, self.mapa.height - alto_visible))

        #---suavizado de camara---
        self.camera_offset += (self.camera_target - self.camera_offset) * self.camera_smoothness * dt

        #---condicion de derrota---
        if not self.player.vivo:
            self.sonido_perder.play()
            self.musica_juego.stop()
            self.estado = "game_over"

    #---funcion para cambiar de nivel---
    #def cambiar_nivel(self, ruta_mapa):

        #---cargar nuevo mapa---
        #self.mapa = Map(ruta_mapa)

        #---actualizar tamaño del tile---
        #self.tile_w = self.mapa.tmx.tilewidth
        #self.tile_h = self.mapa.tmx.tileheight

        #---reiniciar jugador en 17,18---
        #self.player.pos.x = 17 * self.tile_w
        #self.player.pos.y = 17 * self.tile_h
        #self.player.rect.topleft = self.player.pos

        #---resetear camara---
        #self.camera_offset = pygame.Vector2(0, 0)
        #ssself.camera_target = pygame.Vector2(0, 0)

    #---estado game over---
    def estado_game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.jugando = False
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.pantalla_completa = not self.pantalla_completa
                    if self.pantalla_completa:
                        self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.ventana = pygame.display.set_mode((1080, 600), pygame.RESIZABLE)

                #---reiniciar con R---
                if event.key == pygame.K_r:
                    self.iniciar_juego()
                    self.estado = "juego"

                #---volver al menu con ESC---
                if event.key == pygame.K_ESCAPE:
                    self.iniciar_juego()
                    self.estado = "menu"

    #---estado victoria---
    def estado_victoria(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.jugando = False
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.pantalla_completa = not self.pantalla_completa
                    if self.pantalla_completa:
                        self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.ventana = pygame.display.set_mode((1080, 600), pygame.RESIZABLE)

                #---reiniciar con R---
                if event.key == pygame.K_r:
                    self.iniciar_juego()
                    self.estado = "juego"

                #---volver al menu con ESC---
                if event.key == pygame.K_ESCAPE:
                    self.iniciar_juego()
                    self.estado = "menu"

    #---eventos del juego---
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.jugando = False
                sys.exit()

            #---pantalla completa con F11---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.pantalla_completa = not self.pantalla_completa
                    if self.pantalla_completa:
                        self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.ventana = pygame.display.set_mode((1080, 600), pygame.RESIZABLE)
                    self.menu.ventana = self.ventana
                    self.menu.fondo = pygame.transform.scale(
                        self.menu.fondo_original, self.ventana.get_size()
                    )

            self.player.input(event)

    #---dibujo del juego---
    def draw(self):

        if self.estado == "menu":
            self.ventana.fill((0,0,0))
            self.menu.draw()

        elif self.estado == "juego":

            self.ventana.fill((0,0,0))

            ancho_visible = int(self.ventana.get_width() / self.zoom)
            alto_visible = int(self.ventana.get_height() / self.zoom)

            world_surface = pygame.Surface((ancho_visible, alto_visible))

            cam_x = int(self.camera_offset.x)
            cam_y = int(self.camera_offset.y)

            #---dibujar mapa---
            self.mapa.draw(world_surface, pygame.Vector2(cam_x, cam_y))

            #---dibujar jugador---
            if self.player.visible:
                imagen = self.player.image
                if self.player.voltear:
                    imagen = pygame.transform.flip(self.player.image, True, False)
                world_surface.blit(
                    imagen,
                    (
                        self.player.rect.x - cam_x,
                        self.player.rect.y - cam_y
                    )
                )

            #---dibujar esqueletos---
            for esqueleto in self.esqueletos:
                esqueleto.draw(world_surface, cam_x, cam_y)

            #---aplicar zoom---
            scaled = pygame.transform.scale(
                world_surface,
                (self.ventana.get_width(), self.ventana.get_height())
            )

            self.ventana.blit(scaled, (0,0))

            #---dibujar HUD encima de todo (en coordenadas de pantalla)---
            self.hud.draw(self.ventana, self.player.vidas, self.player.vidas_max)

            #---mostrar contador de bajas en pantalla---
            color_contador = (255, 215, 0) if self.esqueletos_eliminados >= 3 else (200, 80, 80)
            texto_bajas = self.fuente_mini.render(
                f"Enemigos: {self.esqueletos_eliminados}/3", True, color_contador
            )
            self.ventana.blit(texto_bajas, (self.ventana.get_width() - texto_bajas.get_width() - 16, 16))

        elif self.estado == "game_over":
            self.ventana.fill((0, 0, 0))
            texto = self.fuente.render("GAME OVER", True, (200, 0, 0))
            sub = self.fuente_pequeña.render("R - Reiniciar     ESC - Menu", True, (180, 180, 180))
            cx = self.ventana.get_width() // 2
            cy = self.ventana.get_height() // 2
            self.ventana.blit(texto, (cx - texto.get_width() // 2, cy - 60))
            self.ventana.blit(sub, (cx - sub.get_width() // 2, cy + 10))

        elif self.estado == "victoria":
            self.ventana.fill((0, 0, 0))
            cx = self.ventana.get_width() // 2
            cy = self.ventana.get_height() // 2
            titulo = self.fuente.render("¡ESCAPASTE!", True, (255, 215, 0))
            frase = self.fuente_pequeña.render("...pero esto no se quedara asi.", True, (200, 200, 200))
            coming = self.fuente_mini.render("— Siguiente nivel: Coming Soon —", True, (120, 120, 120))
            controles = self.fuente_mini.render("R - Reiniciar     ESC - Menu", True, (100, 100, 100))
            self.ventana.blit(titulo, (cx - titulo.get_width() // 2, cy - 80))
            self.ventana.blit(frase, (cx - frase.get_width() // 2, cy - 10))
            self.ventana.blit(coming, (cx - coming.get_width() // 2, cy + 30))
            self.ventana.blit(controles, (cx - controles.get_width() // 2, cy + 70))

        pygame.display.flip()

#---punto de entrada del juego---
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()