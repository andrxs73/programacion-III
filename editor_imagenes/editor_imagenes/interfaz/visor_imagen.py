"""Zona donde se muestra la vista previa, escalada al tamaño disponible."""
from tkinter import ttk

from PIL import ImageTk

MENSAJE_VACIO = "Abre una imagen para comenzar\n(Ctrl + O)"


class VisorImagen(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, width=640, height=520)
        self.pack_propagate(False)  # el tamaño lo define la ventana, no la imagen
        self._imagen = None
        self._foto = None           # referencia necesaria para que Tk no la descarte
        self._etiqueta = ttk.Label(self, anchor="center", justify="center",
                                   font=("Helvetica", 14), foreground="#777777")
        self._etiqueta.pack(fill="both", expand=True)
        self.bind("<Configure>", lambda _evento: self._redibujar())
        self._redibujar()

    def mostrar(self, imagen):
        self._imagen = imagen
        self._redibujar()

    def limpiar(self):
        self._imagen = None
        self._redibujar()

    def _redibujar(self):
        if self._imagen is None:
            self._foto = None
            self._etiqueta.config(image="", text=MENSAJE_VACIO)
            return
        ancho = max(self.winfo_width() - 20, 50)
        alto = max(self.winfo_height() - 20, 50)
        vista = self._imagen.copy()
        vista.thumbnail((ancho, alto))
        self._foto = ImageTk.PhotoImage(vista)
        self._etiqueta.config(image=self._foto, text="")
