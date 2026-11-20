"""Panel lateral con todos los controles. Solo emite eventos: no contiene lógica de edición."""
import tkinter as tk
from tkinter import ttk


class PanelControles(ttk.Frame):
    def __init__(self, master, nombres_filtros, *, al_abrir, al_guardar, al_deshacer,
                 al_restaurar, al_cambiar_filtro, al_aplicar_filtro, al_rotar,
                 al_voltear, al_redimensionar):
        super().__init__(master, padding=10)
        self._hay_imagen = False
        self._puede_deshacer = False
        self._filtro_usa_intensidad = False
        self._edicion = []  # controles que requieren una imagen cargada

        # ----- Archivo e historial (botones en pareja para ahorrar espacio) -----
        archivo = ttk.LabelFrame(self, text="Archivo", padding=6)
        archivo.pack(fill="x", pady=(0, 8))
        fila_archivo = ttk.Frame(archivo)
        fila_archivo.pack(fill="x")
        ttk.Button(fila_archivo, text="Abrir...", width=9, command=al_abrir).pack(
            side="left", padx=2, expand=True, fill="x")
        self._registrar(ttk.Button(fila_archivo, text="Guardar...", width=9, command=al_guardar),
                        fila_archivo, lado="left")

        historial = ttk.LabelFrame(self, text="Historial", padding=6)
        historial.pack(fill="x", pady=(0, 8))
        fila_historial = ttk.Frame(historial)
        fila_historial.pack(fill="x")
        self._boton_deshacer = ttk.Button(fila_historial, text="Deshacer", width=9,
                                          command=al_deshacer)
        self._boton_deshacer.pack(side="left", padx=2, expand=True, fill="x")
        self._registrar(ttk.Button(fila_historial, text="Original", width=9,
                                   command=al_restaurar), fila_historial, lado="left")

        # ----- Filtros -----
        filtros = ttk.LabelFrame(self, text="Filtros", padding=6)
        filtros.pack(fill="x", pady=(0, 8))
        self._filtro = tk.StringVar()
        self._combo = ttk.Combobox(filtros, textvariable=self._filtro, state="readonly",
                                   values=nombres_filtros)
        self._combo.pack(fill="x", pady=2)
        self._combo.bind("<<ComboboxSelected>>", lambda _e: al_cambiar_filtro(self._filtro.get()))
        self._edicion.append(self._combo)

        self._descripcion = ttk.Label(filtros, wraplength=190, foreground="#666666")
        self._descripcion.pack(fill="x", pady=(2, 6))

        self._intensidad = tk.DoubleVar(value=50)
        self._etiqueta_intensidad = ttk.Label(filtros, text="Intensidad: 50")
        self._etiqueta_intensidad.pack(anchor="w")
        self._deslizador = ttk.Scale(filtros, from_=0, to=100, variable=self._intensidad,
                                     command=self._al_mover_deslizador)
        self._deslizador.pack(fill="x", pady=2)
        self._registrar(ttk.Button(filtros, text="Aplicar filtro", command=al_aplicar_filtro),
                        filtros)

        # ----- Transformaciones -----
        transformar = ttk.LabelFrame(self, text="Transformar", padding=6)
        transformar.pack(fill="x")
        fila = ttk.Frame(transformar)
        fila.pack(fill="x")
        self._registrar(ttk.Button(fila, text="↺ 90°", width=7,
                                   command=lambda: al_rotar(90)), fila, lado="left")
        self._registrar(ttk.Button(fila, text="↻ 90°", width=7,
                                   command=lambda: al_rotar(-90)), fila, lado="left")
        self._registrar(ttk.Button(transformar, text="Voltear horizontal", command=al_voltear),
                        transformar)
        ttk.Label(transformar, text="Escala (%):").pack(anchor="w", pady=(8, 0))
        self._escala = tk.StringVar(value="50")
        self._entrada_escala = ttk.Entry(transformar, textvariable=self._escala, width=8)
        self._entrada_escala.pack(anchor="w", pady=2)
        self._edicion.append(self._entrada_escala)
        self._registrar(ttk.Button(transformar, text="Redimensionar",
                                   command=lambda: al_redimensionar(self._escala.get())),
                        transformar)
        self._refrescar_estado()

    # ---------- API pública ----------
    def filtro_seleccionado(self):
        return self._filtro.get()

    def intensidad(self):
        return round(self._intensidad.get())

    def mostrar_filtro(self, filtro):
        """Actualiza descripción y deslizador según el filtro elegido."""
        self._descripcion.config(text=filtro.descripcion)
        self._filtro_usa_intensidad = filtro.usa_intensidad
        if filtro.usa_intensidad:
            self._intensidad.set(filtro.intensidad)
            self._al_mover_deslizador()
        self._refrescar_estado()

    def actualizar_estado(self, hay_imagen, puede_deshacer):
        self._hay_imagen = hay_imagen
        self._puede_deshacer = puede_deshacer
        self._refrescar_estado()

    # ---------- Internos ----------
    def _registrar(self, boton, contenedor, lado=None):
        if lado:
            boton.pack(side=lado, padx=2, pady=2, expand=True, fill="x")
        else:
            boton.pack(fill="x", pady=2)
        self._edicion.append(boton)
        return boton

    def _al_mover_deslizador(self, _valor=None):
        self._etiqueta_intensidad.config(text=f"Intensidad: {self.intensidad()}")

    @staticmethod
    def _poner_estado(control, activo):
        control.state(["!disabled"] if activo else ["disabled"])

    def _refrescar_estado(self):
        for control in self._edicion:
            self._poner_estado(control, self._hay_imagen)
        self._poner_estado(self._boton_deshacer, self._hay_imagen and self._puede_deshacer)
        self._poner_estado(self._deslizador, self._hay_imagen and self._filtro_usa_intensidad)
