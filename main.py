# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

import pygame,sys
from scripts.player import Player
from scripts.menu import Menu
from scripts.map import Map

class Game:
    #---inicializacion---
    def __init__(self):
        pygame.init()
        #---ventana---
        self.ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.pantalla_completa = True
        pygame.display.set_caption("Sangre & Piedra")

        self.reloj = pygame.time.Clock()
        self.jugando = True

        #---zoom---
        self.zoom = 2.5

        #---mapa---
        self.mapa = Map("assets/maps-tiled/mapa_1.tmx")

        #---tamaño del tile---
        self.tile_w = self.mapa.tmx.tilewidth
        self.tile_h = self.mapa.tmx.tileheight

        #---spawn del jugador---
        spawn_x = 17 * self.tile_w
        spawn_y = 17 * self.tile_h
        self.player = Player(spawn_x, spawn_y)

        #---cámara---
        self.camera_offset = pygame.Vector2(0, 0)
        self.camera_target = pygame.Vector2(0, 0)
        self.camera_smoothness = 5  

        #---menu---
        self.menu = Menu(self.ventana, "assets/images/fondo_menu.jpg")
        self.estado = "menu"

    #---bucle principal del juego---
    def run(self):
        while self.jugando:
            #---delta time---
            dt = self.reloj.tick(60) / 1000

            if self.estado == "menu":
                self.estado_menu(dt)

            elif self.estado == "juego":
                self.estado_juego(dt)

            self.draw()

        pygame.quit()
        sys.exit()

    #---estado del menu---
    def estado_menu(self, dt):
        resultado = self.menu.update(dt)

        if resultado == "jugar":
            self.estado = "juego"

        elif resultado == "salir":
            self.jugando = False

    #---estado del juego---
    def estado_juego(self, dt):
        self.events()
        self.player.update(dt, self.mapa.colisiones)

        #---detecta tile actual del jugador---
        tile_x = int(self.player.rect.x // self.tile_w)
        tile_y = int(self.player.rect.y // self.tile_h)

        #---si llega a la posicion 4,1 cambiar nivel---
        #if tile_x == 4 and tile_y == 0:
            #self.cambiar_nivel("assets/maps-tiled/todavia no esta")

        ancho_visible = self.ventana.get_width() / self.zoom
        alto_visible = self.ventana.get_height() / self.zoom

        self.camera_target.x = self.player.rect.centerx - ancho_visible / 2
        self.camera_target.y = self.player.rect.centery - alto_visible / 2

        #---limite de camara---
        self.camera_target.x = max(0, min(self.camera_target.x, self.mapa.width - ancho_visible))
        self.camera_target.y = max(0, min(self.camera_target.y, self.mapa.height - alto_visible))

        #---suavizado de camara---
        self.camera_offset += (self.camera_target - self.camera_offset) * self.camera_smoothness * dt
         
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

    #---eventos del juego---
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.jugando = False
                sys.exit()

            #---toggle pantalla completa con F11---
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

            #---aplicar zoom---
            scaled = pygame.transform.scale(
                world_surface,
                (self.ventana.get_width(), self.ventana.get_height())
            )

            self.ventana.blit(scaled, (0,0))

        pygame.display.flip()
    
#---punto de entrada del juego---
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()