# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

#Recordatorio: para agregar más opciones, simplemente las añado la lista self.opciones y actualizo el método seleccionar() para manejar las nuevas opciones.
#Recordatorio: tengo que cambiar la fuente de texto y buscar un gui para agregarlo 
#Recordatorio: hacer que las opciones interactuen con el mouse

import pygame
import sys

class Menu:

    def __init__(self, ventana, ruta_fondo):
        self.ventana = ventana
        self.fondo_original = pygame.image.load(ruta_fondo).convert()
        self.fondo = pygame.transform.scale(self.fondo_original, self.ventana.get_size())

        self.opcion = 0
        self.opciones = ["Iniciar", "Salir"]

        self.font = pygame.font.SysFont("arial", 40)

    def update(self, dt):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "salir"

            if event.type == pygame.VIDEORESIZE:
                self.ventana = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.fondo = pygame.transform.scale(self.fondo_original, (event.w, event.h))

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_DOWN:
                    self.opcion = (self.opcion + 1) % len(self.opciones)

                if event.key == pygame.K_UP:
                    self.opcion = (self.opcion - 1) % len(self.opciones)

                if event.key == pygame.K_RETURN:
                    return self.seleccionar()

        return None

    def seleccionar(self):

        if self.opcion == 0:
            return "jugar"

        if self.opcion == 1:
            return "salir"

    def draw(self):
        
        self.ventana.blit(self.fondo, (0, 0))

        for i, texto in enumerate(self.opciones):

            color = (255, 255, 255)
            if i == self.opcion:
                color = (200, 50, 50)

            render = self.font.render(texto, True, color)

            x = self.ventana.get_width() // 2 - render.get_width() // 2
            y = self.ventana.get_height() // 2 + i * 60

            self.ventana.blit(render, (x, y))