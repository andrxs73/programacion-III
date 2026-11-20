"""Ventana principal: conecta los eventos de la interfaz con el editor y el catálogo."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from interfaz.panel_controles import PanelControles
from interfaz.visor_imagen import VisorImagen
from servicios.editor_imagen import ImagenInvalidaError, ImagenNoCargadaError

TIPOS_ABRIR = [("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"), ("Todos", "*.*")]
TIPOS_GUARDAR = [("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]


class VentanaPrincipal(tk.Tk):
    def __init__(self, editor, catalogo):
        super().__init__()
        self.title("Editor de Imágenes")
        self.geometry("1000x660")
        self.minsize(860, 640)
        ttk.Style(self).theme_use("clam")

        self._editor = editor        # asociación: la ventana usa al editor
        self._catalogo = catalogo    # asociación: y al catálogo de filtros

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Composición: la ventana crea y es dueña de sus componentes visuales.
        self._panel = PanelControles(
            self, catalogo.nombres(),
            al_abrir=self._abrir, al_guardar=self._guardar,
            al_deshacer=self._deshacer, al_restaurar=self._restaurar,
            al_cambiar_filtro=self._cambiar_filtro, al_aplicar_filtro=self._aplicar_filtro,
            al_rotar=self._rotar, al_voltear=self._voltear,
            al_redimensionar=self._redimensionar)
        self._panel.grid(row=0, column=0, sticky="ns")
        self._visor = VisorImagen(self)
        self._visor.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        self._estado = tk.StringVar(value="Listo.")
        ttk.Label(self, textvariable=self._estado, relief="sunken", anchor="w",
                  padding=(8, 3)).grid(row=1, column=0, columnspan=2, sticky="ew")

        self.bind("<Control-o>", lambda _e: self._abrir())
        self.bind("<Control-s>", lambda _e: self._guardar())
        self.bind("<Control-z>", lambda _e: self._deshacer())
        self._sincronizar()

    # ---------- Sincronización con el modelo ----------
    def _sincronizar(self, mensaje=""):
        e = self._editor
        self._panel.actualizar_estado(e.tiene_imagen, e.puede_deshacer)
        if e.tiene_imagen:
            self._visor.mostrar(e.imagen)
            ancho, alto = e.tamano
            base = f"{e.nombre_archivo}  ·  {ancho}×{alto} px"
            self._estado.set(f"{base}  ·  {mensaje}" if mensaje else base)
        else:
            self._visor.limpiar()
            self._estado.set(mensaje or "Listo.")

    def _ejecutar(self, accion, mensaje):
        """Ejecuta una acción del editor mostrando los errores previsibles al usuario."""
        try:
            accion()
        except (ImagenNoCargadaError, ImagenInvalidaError, ValueError, TypeError) as error:
            messagebox.showerror("No se pudo completar la acción", str(error))
            return
        self._sincronizar(mensaje)

    # ---------- Callbacks ----------
    def _abrir(self):
        ruta = filedialog.askopenfilename(title="Abrir imagen", filetypes=TIPOS_ABRIR)
        if ruta:
            self._ejecutar(lambda: self._editor.cargar(ruta), "imagen cargada")

    def _guardar(self):
        if not self._editor.tiene_imagen:
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar imagen", defaultextension=".png", filetypes=TIPOS_GUARDAR)
        if ruta:
            self._ejecutar(lambda: self._editor.exportar(ruta), "imagen guardada")

    def _deshacer(self):
        if not self._editor.tiene_imagen:
            return
        if self._editor.deshacer():
            self._sincronizar("cambio deshecho")
        else:
            self._estado.set("No hay cambios para deshacer.")

    def _restaurar(self):
        self._ejecutar(self._editor.restaurar, "imagen original restaurada")

    def _cambiar_filtro(self, nombre):
        self._ejecutar(lambda: self._panel.mostrar_filtro(self._catalogo.obtener(nombre)), "")

    def _aplicar_filtro(self):
        nombre = self._panel.filtro_seleccionado()
        if not nombre:
            messagebox.showwarning("Falta el filtro", "Elige un filtro de la lista.")
            return

        def accion():
            filtro = self._catalogo.obtener(nombre)
            if filtro.usa_intensidad:
                filtro.intensidad = self._panel.intensidad()
            self._editor.aplicar_filtro(filtro)

        self._ejecutar(accion, f"filtro «{nombre}» aplicado")

    def _rotar(self, grados):
        self._ejecutar(lambda: self._editor.rotar(grados), "imagen rotada")

    def _voltear(self):
        self._ejecutar(self._editor.voltear_horizontal, "imagen volteada")

    def _redimensionar(self, texto):
        def accion():
            try:
                porcentaje = int(texto)
            except ValueError:
                raise ValueError("La escala debe ser un número entero (por ejemplo, 50).") from None
            self._editor.redimensionar(porcentaje)

        self._ejecutar(accion, "imagen redimensionada")
