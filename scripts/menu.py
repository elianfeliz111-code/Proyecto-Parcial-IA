# Elian Desiderio Feliz Martinez  
# 24-EISN-2-041

import pygame
import sys

class Menu:

    def __init__(self, ventana, ruta_fondo):
        self.ventana = ventana
        self.fondo_original = pygame.image.load(ruta_fondo).convert()
        self.fondo = pygame.transform.scale(self.fondo_original, self.ventana.get_size())

        self.opcion = 0
        self.opciones = ["Iniciar", "Salir"]

        self.font_size_base = 30
        self.ruta_fuente = "assets/fonts/ari-w9500.ttf"

        self.boton_original = pygame.image.load("assets/images/boton.png").convert_alpha()
        self.boton_base_size = (300, 80)

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

    def render_con_espaciado(self, texto, color, size_multiplier, espacio):

        font_size = int(self.font_size_base * size_multiplier)
        font = pygame.font.Font(self.ruta_fuente, font_size)

        letras = []
        ancho_total = 0

        for letra in texto:
            render = font.render(letra, True, color)
            letras.append(render)
            ancho_total += render.get_width() + espacio

        superficie = pygame.Surface((ancho_total, font.get_height()), pygame.SRCALPHA)

        x = 0
        for render in letras:
            superficie.blit(render, (x, 0))
            x += render.get_width() + espacio

        return superficie

    def draw(self):
        
        self.ventana.blit(self.fondo, (0, 0))

        for i, texto in enumerate(self.opciones):

            color = (255, 255, 255)
            size_multiplier = 1
            espacio = 10

            if i == self.opcion:
                color = (160, 160, 160)
                size_multiplier = 1.15
                espacio = 18

            ancho = int(self.boton_base_size[0] * size_multiplier)
            alto = int(self.boton_base_size[1] * size_multiplier)
            boton = pygame.transform.scale(self.boton_original, (ancho, alto))

            render = self.render_con_espaciado(texto, color, size_multiplier, espacio)

            x = self.ventana.get_width() // 2 - boton.get_width() // 2
            y = self.ventana.get_height() // 2 + i * 120

            self.ventana.blit(boton, (x, y))

            tx = x + boton.get_width() // 2 - render.get_width() // 2
            ty = y + boton.get_height() // 2 - render.get_height() // 2

            self.ventana.blit(render, (tx, ty))