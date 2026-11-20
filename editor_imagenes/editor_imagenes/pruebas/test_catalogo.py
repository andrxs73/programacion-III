import pytest

from modelos import FiltroGrises
from servicios.catalogo_filtros import CatalogoFiltros, crear_catalogo_por_defecto


def test_catalogo_por_defecto_tiene_seis_filtros():
    assert len(crear_catalogo_por_defecto().nombres()) == 6


def test_obtener_filtro_inexistente_lanza_error():
    with pytest.raises(ValueError):
        crear_catalogo_por_defecto().obtener("Magia")


def test_no_permite_nombres_repetidos():
    catalogo = CatalogoFiltros([FiltroGrises()])
    with pytest.raises(ValueError):
        catalogo.registrar(FiltroGrises())


def test_solo_registra_filtros():
    with pytest.raises(TypeError):
        CatalogoFiltros().registrar("no soy un filtro")
