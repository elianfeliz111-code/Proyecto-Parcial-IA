# Elian Desiderio Feliz Martinez  
# 24-EISN-2-041

import pygame
from pytmx.util_pygame import load_pygame

class Map:
    def __init__(self, ruta):
        self.tmx = load_pygame(ruta)
        self.width = self.tmx.width * self.tmx.tilewidth
        self.height = self.tmx.height * self.tmx.tileheight

        self.colisiones = []
        self.crear_colisiones()

    def crear_colisiones(self):

        #---obtener la object layer de tiled---
        layer = self.tmx.get_layer_by_name("coliciones")

        for obj in layer:
            rect = pygame.Rect(
                obj.x,
                obj.y,
                obj.width,
                obj.height
            )

            self.colisiones.append(rect)

    def draw(self, surface, camera_offset):
        for layer in self.tmx.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = self.tmx.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(
                            tile,
                            (
                                x * self.tmx.tilewidth - camera_offset.x,
                                y * self.tmx.tileheight - camera_offset.y
                            )
                        )