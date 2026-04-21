import customtkinter as ctk
from src.components.mandatory_field import MandatoryField
from src.components.mandatory_button import MandatoryButton


class UserInput(ctk.CTkFrame):
    """
    Pantalla de login que solicita usuario y contraseña.
    """
    
    def __init__(self, master, on_submit=None, on_cancel=None):
        super().__init__(master, fg_color="#2E1258")
        
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de login."""
        # Frame central
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True)
        
        # Título
        title = ctk.CTkLabel(
            center_frame,
            text="Bienvenido a Impostor TCP",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFD700"
        )
        title.pack(pady=(0, 30))
        
        # Campo de usuario
        self.username_field = MandatoryField(
            master=center_frame,
            label="Usuario",
            expand=True,
            align="center",
            password=False,
            autofocus=True,
            callback=self.on_field_change
        )
        self.username_field.pack(pady=10, padx=40, fill="x")
        
        # Campo de contraseña
        self.password_field = MandatoryField(
            master=center_frame,
            label="Contraseña",
            expand=True,
            align="center",
            password=True,
            autofocus=False,
            callback=self.on_field_change
        )
        self.password_field.pack(pady=10, padx=40, fill="x")
        
        # Botón de submit
        self.submit_button = MandatoryButton(
            master=center_frame,
            text="Ingresar",
            disabled=True,
            align="center",
            on_click=self.on_submit_click
        )
        self.submit_button.pack(pady=20)
    
    def on_field_change(self):
        """Habilita/deshabilita el botón según los campos."""
        if self.username_field.is_unlocked and self.password_field.is_unlocked:
            self.submit_button.unlock()
        else:
            self.submit_button.lock()
    
    def on_submit_click(self):
        """Envía las credenciales al callback."""
        if self.on_submit:
            self.on_submit(
                self.username_field.mandatory_value,
                self.password_field.mandatory_value
            )