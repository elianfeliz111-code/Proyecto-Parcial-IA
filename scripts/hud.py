# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

import pygame

class HUD:

    def __init__(self):
        self.tam = 28
        self.margen = 6
        self.offset_x = 16
        self.offset_y = 16

        corazon_original = pygame.image.load("assets/images/heart.png").convert_alpha()
        self.corazon_lleno = pygame.transform.scale(corazon_original, (self.tam, self.tam))

        #---corazon vacio con efecto oscuro---
        self.corazon_vacio = self.corazon_lleno.copy()
        oscuro = pygame.Surface((self.tam, self.tam), pygame.SRCALPHA)
        oscuro.fill((0, 0, 0, 160))
        self.corazon_vacio.blit(oscuro, (0, 0))

    def draw(self, surface, vidas, vidas_max):
        for i in range(vidas_max):
            x = self.offset_x + i * (self.tam + self.margen)
            y = self.offset_y

            if i < vidas:
                surface.blit(self.corazon_lleno, (x, y))
            else:
                surface.blit(self.corazon_vacio, (x, y))