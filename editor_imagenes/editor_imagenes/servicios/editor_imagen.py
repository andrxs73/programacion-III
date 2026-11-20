"""Lógica de edición: carga, transformaciones, filtros, deshacer y exportación."""
import os

from PIL import Image, ImageOps, UnidentifiedImageError

from modelos import Filtro
from servicios.historial import HistorialCambios


class ImagenNoCargadaError(Exception):
    """Se intentó editar sin haber cargado una imagen."""


class ImagenInvalidaError(Exception):
    """El archivo no existe o no es una imagen que se pueda abrir."""


class EditorImagen:
    """Mantiene la imagen en edición. No conoce nada de la interfaz gráfica."""

    FORMATOS = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".bmp": "BMP"}
    PORCENTAJE_MIN, PORCENTAJE_MAX = 1, 500
    LADO_MAXIMO = 8000

    def __init__(self):
        self._original = None
        self._actual = None
        self._ruta = None
        self._historial = HistorialCambios()  # composición: el editor es dueño del historial

    # ---------- Consulta de estado (solo lectura) ----------
    @property
    def tiene_imagen(self):
        return self._actual is not None

    @property
    def puede_deshacer(self):
        return not self._historial.vacio

    @property
    def nombre_archivo(self):
        return os.path.basename(self._ruta) if self._ruta else ""

    @property
    def tamano(self):
        self._requerir_imagen()
        return self._actual.size

    @property
    def imagen(self):
        """Copia de la imagen actual: el exterior no puede modificar el estado interno."""
        self._requerir_imagen()
        return self._actual.copy()

    # ---------- Operaciones ----------
    def cargar(self, ruta):
        try:
            with Image.open(ruta) as archivo:
                archivo.load()
                imagen = ImageOps.exif_transpose(archivo).convert("RGB")
        except (OSError, UnidentifiedImageError, ValueError) as error:
            raise ImagenInvalidaError(
                "No se pudo abrir el archivo. Verifica que exista y que sea una imagen válida."
            ) from error
        self._original = imagen
        self._actual = imagen.copy()
        self._ruta = ruta
        self._historial.limpiar()

    def aplicar_filtro(self, filtro):
        self._requerir_imagen()
        if not isinstance(filtro, Filtro):
            raise TypeError("Solo se pueden aplicar objetos de tipo Filtro.")
        self._registrar_cambio(filtro.aplicar(self._actual))

    def rotar(self, grados):
        """Rota en sentido antihorario. Solo admite múltiplos de 90."""
        self._requerir_imagen()
        if grados % 90 != 0:
            raise ValueError("Solo se puede rotar en múltiplos de 90 grados.")
        self._registrar_cambio(self._actual.rotate(grados, expand=True))

    def voltear_horizontal(self):
        self._requerir_imagen()
        self._registrar_cambio(ImageOps.mirror(self._actual))

    def redimensionar(self, porcentaje):
        self._requerir_imagen()
        if not self.PORCENTAJE_MIN <= porcentaje <= self.PORCENTAJE_MAX:
            raise ValueError(
                f"El porcentaje debe estar entre {self.PORCENTAJE_MIN} y {self.PORCENTAJE_MAX}.")
        ancho, alto = self._actual.size
        nuevo = (max(1, round(ancho * porcentaje / 100)), max(1, round(alto * porcentaje / 100)))
        if max(nuevo) > self.LADO_MAXIMO:
            raise ValueError(f"La imagen resultante superaría {self.LADO_MAXIMO} px por lado.")
        self._registrar_cambio(self._actual.resize(nuevo, Image.LANCZOS))

    def deshacer(self):
        """Vuelve al estado anterior. Devuelve False si no había nada que deshacer."""
        self._requerir_imagen()
        anterior = self._historial.deshacer()
        if anterior is None:
            return False
        self._actual = anterior
        return True

    def restaurar(self):
        """Vuelve a la imagen original (el cambio también se puede deshacer)."""
        self._requerir_imagen()
        self._registrar_cambio(self._original.copy())

    def exportar(self, ruta):
        self._requerir_imagen()
        extension = os.path.splitext(ruta)[1].lower()
        if extension not in self.FORMATOS:
            raise ValueError("Formato no soportado. Usa .png, .jpg o .bmp.")
        try:
            self._actual.save(ruta, self.FORMATOS[extension])
        except OSError as error:
            raise ValueError(f"No se pudo guardar el archivo: {error}") from error

    # ---------- Auxiliares internos ----------
    def _requerir_imagen(self):
        if self._actual is None:
            raise ImagenNoCargadaError("Primero abre una imagen.")

    def _registrar_cambio(self, nueva):
        self._historial.apilar(self._actual)
        self._actual = nueva
