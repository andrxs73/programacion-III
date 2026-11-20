"""Punto de entrada de la aplicación."""
from interfaz.ventana_principal import VentanaPrincipal
from servicios.catalogo_filtros import crear_catalogo_por_defecto
from servicios.editor_imagen import EditorImagen


def main():
    VentanaPrincipal(EditorImagen(), crear_catalogo_por_defecto()).mainloop()


if __name__ == "__main__":
    main()
