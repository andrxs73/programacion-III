"""Pila limitada de estados anteriores de la imagen, para poder deshacer."""
from collections import deque


class HistorialCambios:
    def __init__(self, limite=10):
        if limite < 1:
            raise ValueError("El límite del historial debe ser al menos 1.")
        self._pila = deque(maxlen=limite)

    def __len__(self):
        return len(self._pila)

    @property
    def vacio(self):
        return not self._pila

    def apilar(self, imagen):
        self._pila.append(imagen.copy())

    def deshacer(self):
        """Devuelve el estado anterior o None si no hay nada que deshacer."""
        return self._pila.pop() if self._pila else None

    def limpiar(self):
        self._pila.clear()
