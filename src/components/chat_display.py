import customtkinter as ctk
from src.components.mandatory_field import MandatoryField
from src.components.mandatory_button import MandatoryButton
from src.classes.player import Player


class ChatDisplay(ctk.CTkFrame):
    """
    Componente de chat con auto-scroll (versión completamente sincrónica).
    """

    def __init__(self, master, player: Player):
        super().__init__(master)

        self.__player: Player = None
        self.player = player
        self._messages = []

        # Configuración principal
        self.configure(fg_color="transparent")
        self.pack(fill="both", expand=True)

        # Título
        self._setup_title()

        # Área de mensajes
        self._setup_messages_area()

        # Área de entrada
        self._setup_input_area()

    def _setup_title(self):
        """Configura el título del chat."""
        self.title_label = ctk.CTkLabel(
            self,
            text="💬 CHAT ZONE",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#7357FF"
        )
        self.title_label.pack(pady=(0, 10))

    def _setup_messages_area(self):
        """Configura el área scrollable de mensajes."""
        self.messages_container = ctk.CTkScrollableFrame(
            self,
            fg_color="#1E1E1E",
            corner_radius=10,
            border_width=0,
            label_text="",
            orientation="vertical"
        )
        self.messages_container.pack(pady=10, padx=10, fill="both", expand=True)

        # Frame contenedor interno
        self.messages_column = ctk.CTkFrame(
            self.messages_container,
            fg_color="transparent"
        )
        self.messages_column.pack(fill="x", expand=True)

    def _setup_input_area(self):
        """Configura el área de entrada de mensajes."""
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(pady=(10, 0), padx=10, fill="x")

        # Campo de mensaje
        self.message_field = MandatoryField(
            master=input_frame,
            label="Escribe tu mensaje...",
            expand=True,
            password=False,
            autofocus=True,
            callback=self.__callback_message_field
        )
        self.message_field.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Botón de enviar
        self.send_button = MandatoryButton(
            master=input_frame,
            text="📤 Enviar",
            disabled=True,
            align="center",
            on_click=self.__on_click_send_button
        )
        self.send_button.pack(side="right")

        # Bind para enviar con Enter
        self.message_field.bind("<Return>", self.__on_enter_pressed)

    @property
    def player(self) -> Player:
        return self.__player

    @player.setter
    def player(self, player: Player) -> None:
        if isinstance(player, Player):
            self.__player = player

    def __build_message(self, player: str, message: str, is_me: bool):
        """Construye un mensaje visualmente."""
        # Crear frame del mensaje
        message_frame = ctk.CTkFrame(
            self.messages_column,
            fg_color="#7357FF" if is_me else "#2D2D2D",
            corner_radius=12,
            border_width=0
        )

        # Configurar alineación
        padding = {"pady": 5, "padx": 10}
        if is_me:
            message_frame.pack(anchor="e", **padding)
        else:
            message_frame.pack(anchor="w", **padding)

        # Nombre del jugador
        player_label = ctk.CTkLabel(
            message_frame,
            text=f"👤 {player}" if not is_me else "TÚ",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#7357FF" if is_me else "#AAAAAA"
        )
        player_label.pack(anchor="w", padx=12, pady=(8, 0))

        # Mensaje
        message_label = ctk.CTkLabel(
            message_frame,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color="#FFFFFF",
            wraplength=280,
            justify="left"
        )
        message_label.pack(anchor="w", padx=12, pady=(0, 8))

        return message_frame

    def add_player_message(self, player: str, message: str):
        """Agrega un nuevo mensaje al chat con auto-scroll."""
        if not message or not message.strip():
            return

        is_me = player == self.player.username

        # Guardar mensaje
        self._messages.append({
            "player": player,
            "message": message,
            "is_me": is_me
        })

        # Crear y agregar el widget del mensaje
        self.__build_message(player, message, is_me)

        # Forzar actualización y scroll automático
        self.messages_column.update_idletasks()
        self._scroll_to_bottom()

        # Limpiar campo de texto
        self.message_field.clear()

    def _scroll_to_bottom(self):
        """Hace scroll automático al final del chat."""
        try:
            # Obtener el canvas del scrollable frame
            if hasattr(self.messages_container, '_parent_canvas'):
                canvas = self.messages_container._parent_canvas
                if canvas:
                    canvas.yview_moveto(1.0)
            # También intentar con el método estándar
            self.messages_container._parent_canvas.yview_moveto(1.0)
        except Exception:
            # Si falla, intentar con after para dar tiempo a que se dibuje
            self.after(10, lambda: self._scroll_to_bottom_retry())

    def _scroll_to_bottom_retry(self):
        """Intento de scroll con retry."""
        try:
            if hasattr(self.messages_container, '_parent_canvas'):
                self.messages_container._parent_canvas.yview_moveto(1.0)
        except:
            pass

    def __on_click_send_button(self):
        """Maneja el envío de mensajes (versión sincrónica)."""
        if self.message_field.is_unlocked:
            message = self.message_field.mandatory_value
            if message:  # Evitar mensajes vacíos
                self.add_player_message(self.player.username, message)
                self.message_field.focus_set()


    def __on_enter_pressed(self, event):
        """Maneja la tecla Enter."""
        self.__on_click_send_button()
        return "break"  # Prevenir comportamiento por defecto

    def __callback_message_field(self):
        """Habilita/deshabilita el botón según el contenido."""
        if self.message_field.is_unlocked:
            self.send_button.unlock()
        else:
            self.send_button.lock()

    def clear_chat(self):
        """Limpia todos los mensajes del chat."""
        for widget in self.messages_column.winfo_children():
            widget.destroy()
        self._messages.clear()

    def get_message_history(self):
        """Retorna el historial de mensajes."""
        return self._messages.copy()