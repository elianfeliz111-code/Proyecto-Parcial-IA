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

        # mapa
        self.mapa = Map("assets/maps-tiled/mapa_1.tmx")

        # jugador
        self.player = Player(100, 100)

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
         
#eventos del juego
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.jugando = False
                sys.exit()
            self.player.input(event)

#dibujo del juego
    def draw(self):
        self.ventana.fill((0, 0, 0))

        if self.estado == "menu":
            self.menu.draw()

        elif self.estado == "juego":
            self.mapa.draw(self.ventana)
            self.player.draw(self.ventana)

        pygame.display.flip()
    
#punto de entrada del juego
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()