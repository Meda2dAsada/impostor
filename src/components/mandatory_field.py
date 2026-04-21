import customtkinter as ctk

class MandatoryField(ctk.CTkEntry):
    """
    Campo de texto con validación automática y cambio de color de borde.
    - Verde: valor válido (no vacío)
    - Rojo: valor inválido (vacío) pero el usuario ha escrito algo
    - Naranja: valor vacío y sin interacción
    """

    def __init__(
        self,
        master,
        label: str = None,
        expand: bool = None,  # En customtkinter se usa width/height o pack(fill=...)
        align: str = None,    # Se mapea a justify
        password: bool = None,
        autofocus: bool = None,
        callback=None,        # En customtkinter no recibe evento automáticamente
    ):
        # Mapeo de alineación (Flet -> customtkinter)
        justify_map = {
            "left": "left",
            "center": "center",
            "right": "right",
        }
        justify = justify_map.get(align, "left") if align else "left"

        # Configuración inicial
        super().__init__(
            master,
            placeholder_text=label if label else "",  # customtkinter no tiene "label", usamos placeholder
            show="*" if password else None,           # Para campos de contraseña
            justify=justify,
            border_color="#FF8000",                   # Color de borde inicial (naranja)
            border_width=2,
            corner_radius=4,
        )

        # Guardar referencia al callback
        self.callback = callback

        # Variables de estado
        self._user_interacted = False  # Para saber si el usuario ya escribió algo

        # Vincular eventos
        self.bind("<KeyRelease>", self._on_self_change)
        self.bind("<FocusOut>", self._on_self_blur)

        # Autofocus si está habilitado
        if autofocus:
            self.focus_set()

        # Aplicar expansión si se solicita (expand=True -> ancho máximo en su contenedor)
        if expand:
            self.pack(fill="x", expand=True)

    def _on_self_change(self, event=None):
        """Se ejecuta cuando el usuario escribe en el campo."""
        self._user_interacted = True
        self._change_border_color_based_on_value()

        if self.callback:
            self.callback()  # Nota: en customtkinter no pasa evento, solo ejecuta la función

    def _on_self_blur(self, event=None):
        """Se ejecuta cuando el campo pierde el foco."""
        if not self.is_unlocked and self._user_interacted:
            self._change_border_color("#FF8000")

    def _change_border_color_based_on_value(self):
        """Cambia el color del borde según el estado del valor."""
        if self.is_unlocked:
            self._change_border_color("#00FF00")  # Verde: valor válido
        elif self._user_interacted:
            self._change_border_color("#FF0000")  # Rojo: valor inválido pero el usuario interactuó
        else:
            self._change_border_color("#FF8000")  # Naranja: estado neutral

    def _change_border_color(self, color: str):
        """Cambia el color del borde del campo."""
        self.configure(border_color=color)

    @property
    def is_unlocked(self) -> bool:
        """Indica si el campo tiene un valor válido (no vacío)."""
        return bool(self.mandatory_value)

    @property
    def mandatory_value(self) -> str:
        """Retorna el valor del campo sin espacios en blanco."""
        return self.get().strip()

    def clear(self):
        """Limpia el campo y resetea los estados."""
        self.delete(0, "end")  # Borra todo el contenido
        self._user_interacted = False
        self._change_border_color("#FF8000")

        if self.callback:
            self.callback()