import pytest
from PIL import Image

from modelos import FiltroGrises
from servicios.editor_imagen import EditorImagen, ImagenInvalidaError, ImagenNoCargadaError
from servicios.historial import HistorialCambios


@pytest.fixture
def editor(tmp_path):
    ruta = tmp_path / "foto.png"
    Image.new("RGB", (40, 20), (200, 50, 50)).save(ruta)
    e = EditorImagen()
    e.cargar(str(ruta))
    return e


def test_cargar_actualiza_el_estado(editor):
    assert editor.tiene_imagen
    assert editor.tamano == (40, 20)
    assert editor.nombre_archivo == "foto.png"
    assert not editor.puede_deshacer


def test_cargar_archivo_inexistente_lanza_error():
    with pytest.raises(ImagenInvalidaError):
        EditorImagen().cargar("no_existe.png")


def test_cargar_archivo_que_no_es_imagen_lanza_error(tmp_path):
    ruta = tmp_path / "texto.png"
    ruta.write_text("esto no es una imagen")
    with pytest.raises(ImagenInvalidaError):
        EditorImagen().cargar(str(ruta))


def test_editar_sin_imagen_lanza_error():
    with pytest.raises(ImagenNoCargadaError):
        EditorImagen().rotar(90)


def test_rotar_90_intercambia_ancho_y_alto(editor):
    editor.rotar(90)
    assert editor.tamano == (20, 40)


def test_rotar_con_angulo_invalido_lanza_error(editor):
    with pytest.raises(ValueError):
        editor.rotar(45)


def test_redimensionar_al_50_por_ciento(editor):
    editor.redimensionar(50)
    assert editor.tamano == (20, 10)


@pytest.mark.parametrize("porcentaje", [0, -5, 501])
def test_redimensionar_porcentaje_invalido(editor, porcentaje):
    with pytest.raises(ValueError):
        editor.redimensionar(porcentaje)


def test_deshacer_recupera_el_estado_anterior(editor):
    editor.redimensionar(50)
    assert editor.deshacer() is True
    assert editor.tamano == (40, 20)
    assert editor.deshacer() is False


def test_restaurar_vuelve_al_original_y_se_puede_deshacer(editor):
    editor.redimensionar(200)
    editor.restaurar()
    assert editor.tamano == (40, 20)
    editor.deshacer()
    assert editor.tamano == (80, 40)


def test_aplicar_filtro_rechaza_objetos_que_no_son_filtros(editor):
    with pytest.raises(TypeError):
        editor.aplicar_filtro("grises")


def test_aplicar_filtro_registra_cambio(editor):
    editor.aplicar_filtro(FiltroGrises())
    assert editor.puede_deshacer


def test_imagen_devuelve_copia_protegida(editor):
    editor.imagen.putpixel((0, 0), (0, 0, 0))
    assert editor.imagen.getpixel((0, 0)) == (200, 50, 50)


def test_exportar_png_y_rechazar_formato_invalido(editor, tmp_path):
    salida = tmp_path / "salida.png"
    editor.exportar(str(salida))
    assert Image.open(salida).size == (40, 20)
    with pytest.raises(ValueError):
        editor.exportar(str(tmp_path / "salida.txt"))


def test_historial_respeta_su_limite():
    historial = HistorialCambios(limite=3)
    for _ in range(5):
        historial.apilar(Image.new("RGB", (2, 2)))
    assert len(historial) == 3
