"""Colección de filtros disponibles para el usuario."""
from modelos import (
    Filtro, FiltroBrillo, FiltroContraste, FiltroDesenfoque,
    FiltroGrises, FiltroInvertir, FiltroSepia,
)


class CatalogoFiltros:
    """Agregación: guarda filtros que existen independientemente del catálogo."""

    def __init__(self, filtros=None):
        self._filtros = {}
        for filtro in filtros or []:
            self.registrar(filtro)

    def registrar(self, filtro):
        if not isinstance(filtro, Filtro):
            raise TypeError("Solo se pueden registrar objetos de tipo Filtro.")
        if filtro.nombre in self._filtros:
            raise ValueError(f"Ya existe un filtro llamado '{filtro.nombre}'.")
        self._filtros[filtro.nombre] = filtro

    def nombres(self):
        return list(self._filtros)

    def obtener(self, nombre):
        try:
            return self._filtros[nombre]
        except KeyError:
            raise ValueError(f"No existe el filtro '{nombre}'.") from None


def crear_catalogo_por_defecto():
    return CatalogoFiltros([
        FiltroGrises(), FiltroSepia(), FiltroInvertir(),
        FiltroDesenfoque(), FiltroBrillo(), FiltroContraste(),
    ])
