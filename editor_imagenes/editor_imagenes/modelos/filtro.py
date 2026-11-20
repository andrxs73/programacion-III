"""Filtros de imagen. Todos cumplen el contrato definido por la clase abstracta Filtro."""
from abc import ABC, abstractmethod

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class Filtro(ABC):
    """Contrato común: cada filtro sabe aplicarse a una imagen y devolver una nueva."""

    #: Indica si el filtro responde al deslizador de intensidad de la interfaz.
    usa_intensidad = False
    descripcion = ""

    def __init__(self, nombre, intensidad=50):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El filtro necesita un nombre.")
        self._nombre = nombre.strip()
        self.intensidad = intensidad  # pasa por el setter con validación

    @property
    def nombre(self):
        return self._nombre

    @property
    def intensidad(self):
        return self._intensidad

    @intensidad.setter
    def intensidad(self, valor):
        es_numero = isinstance(valor, (int, float)) and not isinstance(valor, bool)
        if not es_numero or not 0 <= valor <= 100:
            raise ValueError("La intensidad debe ser un número entre 0 y 100.")
        self._intensidad = valor

    @abstractmethod
    def aplicar(self, imagen):
        """Devuelve una imagen nueva con el filtro aplicado (sin modificar la original)."""


class FiltroGrises(Filtro):
    descripcion = "Convierte la imagen a tonos de gris."

    def __init__(self):
        super().__init__("Escala de grises")

    def aplicar(self, imagen):
        return ImageOps.grayscale(imagen).convert("RGB")


class FiltroInvertir(Filtro):
    descripcion = "Invierte los colores (efecto negativo)."

    def __init__(self):
        super().__init__("Negativo")

    def aplicar(self, imagen):
        return ImageOps.invert(imagen)


class FiltroSepia(Filtro):
    usa_intensidad = True
    descripcion = "Tono marrón cálido. La intensidad mezcla con la imagen original."

    def __init__(self):
        super().__init__("Sepia", intensidad=100)

    def aplicar(self, imagen):
        gris = ImageOps.grayscale(imagen)
        sepia = ImageOps.colorize(gris, black="#1e1208", mid="#a0714a", white="#fff1d6")
        return Image.blend(imagen, sepia, self.intensidad / 100)


class FiltroDesenfoque(Filtro):
    usa_intensidad = True
    descripcion = "Suaviza la imagen. A mayor intensidad, más desenfoque."

    def __init__(self):
        super().__init__("Desenfoque", intensidad=30)

    def aplicar(self, imagen):
        radio = self.intensidad / 10
        if radio == 0:
            return imagen.copy()
        return imagen.filter(ImageFilter.GaussianBlur(radio))


class FiltroAjuste(Filtro, ABC):
    """Clase intermedia (también abstracta) para filtros que realzan una propiedad.

    Con intensidad 50 no cambia nada; por debajo reduce y por encima aumenta.
    """

    usa_intensidad = True

    def _factor(self):
        return 0.5 + self.intensidad / 100

    @abstractmethod
    def _crear_realzador(self, imagen):
        """Devuelve el objeto ImageEnhance que corresponde a la propiedad ajustada."""

    def aplicar(self, imagen):
        return self._crear_realzador(imagen).enhance(self._factor())


class FiltroBrillo(FiltroAjuste):
    descripcion = "Aclara u oscurece. 50 = sin cambios."

    def __init__(self):
        super().__init__("Brillo")

    def _crear_realzador(self, imagen):
        return ImageEnhance.Brightness(imagen)


class FiltroContraste(FiltroAjuste):
    descripcion = "Aumenta o reduce el contraste. 50 = sin cambios."

    def __init__(self):
        super().__init__("Contraste")

    def _crear_realzador(self, imagen):
        return ImageEnhance.Contrast(imagen)
