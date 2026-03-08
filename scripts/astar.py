# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

import heapq

def heuristica(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(inicio, destino, colisiones_set, tile_w, tile_h, max_nodos=200):
    inicio_tile = (int(inicio[0] // tile_w), int(inicio[1] // tile_h))
    destino_tile = (int(destino[0] // tile_w), int(destino[1] // tile_h))

    if inicio_tile == destino_tile:
        return []

    abiertos = []
    heapq.heappush(abiertos, (0, inicio_tile))

    origen = {}
    costo_g = {inicio_tile: 0}
    explorados = 0

    while abiertos:
        # ---limite para evitar congelamiento---
        if explorados > max_nodos:
            break
        explorados += 1

        _, actual = heapq.heappop(abiertos)

        if actual == destino_tile:
            camino = []
            while actual in origen:
                camino.append((
                    actual[0] * tile_w + tile_w // 2,
                    actual[1] * tile_h + tile_h // 2
                ))
                actual = origen[actual]
            camino.reverse()
            return camino

        vecinos = [
            (actual[0]+1, actual[1]),
            (actual[0]-1, actual[1]),
            (actual[0], actual[1]+1),
            (actual[0], actual[1]-1),
        ]

        for vecino in vecinos:
            if vecino in colisiones_set:
                continue

            nuevo_costo = costo_g[actual] + 1

            if vecino not in costo_g or nuevo_costo < costo_g[vecino]:
                costo_g[vecino] = nuevo_costo
                prioridad = nuevo_costo + heuristica(vecino, destino_tile)
                heapq.heappush(abiertos, (prioridad, vecino))
                origen[vecino] = actual

    return []