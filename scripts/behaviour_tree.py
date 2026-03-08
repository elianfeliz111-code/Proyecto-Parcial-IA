# Elian Desiderio Feliz Martinez
# 24-EISN-2-041

SUCCESS = "SUCCESS"
FAILURE = "FAILURE"
RUNNING = "RUNNING"

class Nodo:
    def ejecutar(self):
        raise NotImplementedError

class Secuencia(Nodo):
    
    #---ejecuta hijos en orden, falla si alguno falla---
    def __init__(self, hijos):
        self.hijos = hijos

    def ejecutar(self):
        for hijo in self.hijos:
            resultado = hijo.ejecutar()
            if resultado == FAILURE:
                return FAILURE
            if resultado == RUNNING:
                return RUNNING
        return SUCCESS

class Selector(Nodo):

    #---ejecuta hijos en orden, tiene exito si alguno tiene exito---
    def __init__(self, hijos):
        self.hijos = hijos

    def ejecutar(self):
        for hijo in self.hijos:
            resultado = hijo.ejecutar()
            if resultado == SUCCESS:
                return SUCCESS
            if resultado == RUNNING:
                return RUNNING
        return FAILURE

class Accion(Nodo):
    def __init__(self, funcion):
        self.funcion = funcion

    def ejecutar(self):
        return self.funcion()

class Condicion(Nodo):
    def __init__(self, funcion):
        self.funcion = funcion

    def ejecutar(self):
        return SUCCESS if self.funcion() else FAILURE