import pygame,sys

class Game:
#inicialización del juego
    def __init__(self):
        pygame.init()
        self.ventana = pygame.display.set_mode((1080,600))
        pygame.display.set_caption("Sangre & Piedra")
        self.reloj = pygame.time.Clock()
        self.jugando = True

#bucle principal del juego
    def run(self):
        while self.jugando:
            self.events()
            self.draw()
            self.reloj.tick(60)

#eventos del juego
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.jugando = False
                sys.exit()

#dibujo del juego
    def draw(self):
        self.ventana.fill((0,0,0))
        pygame.display.flip()
    
#punto de entrada del juego
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()