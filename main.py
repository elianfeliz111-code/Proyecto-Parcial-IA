# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

#Recordatorio: variables vida y ataque y daño para el jugador
#Recordatorio: agregar enemigos 
#Recordatorio - importante: arbol de Comportamiento y un algoritmo A* para los enemigos

import pygame,sys
from scripts.player import Player
from scripts.menu import Menu
from scripts.map import Map

class Game:
#inicialización del juego
    def __init__(self):
        pygame.init()

        self.ventana = pygame.display.set_mode((1080,600), pygame.RESIZABLE)
        pygame.display.set_caption("Sangre & Piedra")

        self.reloj = pygame.time.Clock()
        self.jugando = True

        # zoom
        self.zoom = 2.5

        # mapa
        self.mapa = Map("assets/maps-tiled/mapa_1.tmx")

        # jugador
        self.player = Player(100, 100)

        # cámara
        self.camera_offset = pygame.Vector2(0, 0)
        self.camera_target = pygame.Vector2(0, 0)
        self.camera_smoothness = 5  

        self.menu = Menu(self.ventana, "assets/images/fondo_menu.jpg")
        self.estado = "menu"

#bucle principal del juego
    def run(self):
        while self.jugando:

            dt = self.reloj.tick(60) / 1000

            if self.estado == "menu":
                self.estado_menu(dt)

            elif self.estado == "juego":
                self.estado_juego(dt)

            self.draw()

        pygame.quit()
        sys.exit()

#estado del menu
    def estado_menu(self, dt):
        resultado = self.menu.update(dt)

        if resultado == "jugar":
            self.estado = "juego"

        elif resultado == "salir":
            self.jugando = False

#estado del juego
    def estado_juego(self, dt):
        self.events()
        self.player.update(dt)

        ancho_visible = self.ventana.get_width() / self.zoom
        alto_visible = self.ventana.get_height() / self.zoom

        self.camera_target.x = self.player.rect.centerx - ancho_visible / 2
        self.camera_target.y = self.player.rect.centery - alto_visible / 2

        #limite de camara
        self.camera_target.x = max(0, min(self.camera_target.x, self.mapa.width - ancho_visible))
        self.camera_target.y = max(0, min(self.camera_target.y, self.mapa.height - alto_visible))

        #suavizado
        self.camera_offset += (self.camera_target - self.camera_offset) * self.camera_smoothness * dt
         
#eventos del juego
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.jugando = False
                sys.exit()
            self.player.input(event)

#dibujo del juego
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

            #dibujar mapa
            self.mapa.draw(world_surface, pygame.Vector2(cam_x, cam_y))

            #dibujar jugador
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

            #aplicar zoom
            scaled = pygame.transform.scale(
                world_surface,
                (self.ventana.get_width(), self.ventana.get_height())
            )

            self.ventana.blit(scaled, (0,0))

        pygame.display.flip()
    
#punto de entrada del juego
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()