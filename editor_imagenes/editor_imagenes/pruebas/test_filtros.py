import pytest
from PIL import Image, ImageChops, ImageStat

from modelos import (
    Filtro, FiltroAjuste, FiltroBrillo, FiltroContraste, FiltroDesenfoque,
    FiltroGrises, FiltroInvertir, FiltroSepia,
)


def imagen_color():
    img = Image.new("RGB", (20, 10), (200, 80, 40))
    img.putpixel((0, 0), (10, 200, 90))
    return img


def iguales(a, b):
    return ImageChops.difference(a, b).getbbox() is None


def test_clases_abstractas_no_se_pueden_instanciar():
    with pytest.raises(TypeError):
        Filtro("x")
    with pytest.raises(TypeError):
        FiltroAjuste("x")


def test_grises_deja_los_tres_canales_iguales():
    resultado = FiltroGrises().aplicar(imagen_color())
    r, g, b = resultado.split()
    assert iguales(r, g) and iguales(g, b)


def test_negativo_aplicado_dos_veces_devuelve_la_original():
    original = imagen_color()
    filtro = FiltroInvertir()
    assert iguales(filtro.aplicar(filtro.aplicar(original)), original)


def test_los_filtros_no_modifican_la_imagen_original():
    original = imagen_color()
    copia = original.copy()
    for filtro in (FiltroGrises(), FiltroSepia(), FiltroInvertir(),
                   FiltroDesenfoque(), FiltroBrillo(), FiltroContraste()):
        filtro.aplicar(original)
    assert iguales(original, copia)


def test_sepia_con_intensidad_cero_no_cambia_la_imagen():
    filtro = FiltroSepia()
    filtro.intensidad = 0
    original = imagen_color()
    assert iguales(filtro.aplicar(original), original)


def test_brillo_neutro_a_50_y_aumenta_a_100():
    original = Image.new("RGB", (8, 8), (100, 100, 100))
    filtro = FiltroBrillo()
    filtro.intensidad = 50
    assert iguales(filtro.aplicar(original), original)
    filtro.intensidad = 100
    assert ImageStat.Stat(filtro.aplicar(original)).mean[0] > 100


def test_desenfoque_conserva_el_tamano():
    assert FiltroDesenfoque().aplicar(imagen_color()).size == (20, 10)


@pytest.mark.parametrize("valor", [-1, 101, "alto", None, True])
def test_intensidad_invalida_lanza_error(valor):
    with pytest.raises(ValueError):
        FiltroContraste().intensidad = valor


def test_polimorfismo_todos_responden_a_aplicar():
    for filtro in (FiltroGrises(), FiltroSepia(), FiltroInvertir(),
                   FiltroDesenfoque(), FiltroBrillo(), FiltroContraste()):
        assert filtro.aplicar(imagen_color()).size == (20, 10)
