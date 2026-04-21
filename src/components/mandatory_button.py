import customtkinter as ctk
from src.constants.const import MandatoryButtonColors   # Asegúrate de que este enum exista
# Si no existe, puedes definirlo así (ejemplo):
# from enum import Enum
# class MandatoryButtonColors:
#     '#4d185a' = "#0078D4"
#     '#00cc00' = "#FFFFFF"
#     '#5c1c6b' = "#106EBE"


class MandatoryButton(ctk.CTkButton):
    """
    Botón estilo TextButton (plano) con colores basados en 
    Soporta estado disabled, colores específicos para cada estado, y métodos lock/unlock.
    """

    def __init__(
        self,
        master,
        text: str,
        disabled: bool = True,
        align: str = None,
        on_click=None,  # En customtkinter no recibe evento automáticamente
    ):
        # Mapeo de alineación (Flet -> customtkinter)
        anchor_map = {
            "left": "w",
            "center": "center",
            "right": "e",
        }
        anchor = anchor_map.get(align, "center") if align else "center"

        # Configuración inicial (estado normal)
        super().__init__(
            master,
            text=text,
            command=on_click,
            state="disabled" if disabled else "normal",
            anchor=anchor,
            fg_color='#4d185a',
            text_color='#00cc00',
            hover_color='#5c1c6b',
            # Para simular un TextButton (sin bordes, fondo liso)
            border_width=0,
            corner_radius=2,  # opcional, similar a Flet
        )

        # Guardamos colores para poder alternar entre normal/disabled
        self._normal_bg = '#4d185a'
        self._normal_text = '#00cc00'
        self._disabled_bg = "#333333"
        self._disabled_text = "#555555"

        # Aplicar colores de disabled si es necesario
        if disabled:
            self._apply_disabled_style()

    def _apply_disabled_style(self):
        """Cambia colores al estado disabled."""
        self.configure(
            fg_color=self._disabled_bg,
            text_color=self._disabled_text,
            state="disabled",
        )

    def _apply_normal_style(self):
        """Restaura colores al estado normal."""
        self.configure(
            fg_color=self._normal_bg,
            text_color=self._normal_text,
            state="normal",
        )

    def lock(self):
        """Deshabilita el botón y aplica estilo disabled."""
        self._apply_disabled_style()

    def unlock(self):
        """Habilita el botón y restaura estilo normal."""
        self._apply_normal_style()