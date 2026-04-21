import time
import threading
import customtkinter as ctk
from src.constants.const import VisualRole
from src.components.mandatory_field import MandatoryField


class RoleDisplay(ctk.CTkToplevel):
    """
    Diálogo de rol con barra de progreso y campo de texto para enviar palabra.
    """
    
    def __init__(self, master, role: str, word: str | None = None, on_word_sent=None):
        super().__init__(master)
        
        # Configurar ventana
        self.title("🎭 Asignación de Rol")
        self.configure(fg_color="#2E1258")
        self.geometry("550x550")
        self.resizable(False, False)
        
        # Hacer modal
        self.transient(master)
        self.grab_set()
        
        # Variables
        self.role = role
        self.word = word
        self.on_word_sent = on_word_sent  # Callback para enviar la palabra al servidor
        self.running = True
        self.word_sent = False
        
        # Obtener colores según el rol
        self.color_style = VisualRole.get_color(role)
        self.bg_color = VisualRole.get_bgcolor(role)
        
        # Obtener la instrucción/pista según el rol
        self.word_hint = VisualRole.get_word_hint(role)
        
        self._setup_ui()
        
        # Iniciar temporizador
        self._start_unlock_timer()
        
        # Manejar cierre
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo."""
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Icono según rol
        if "IMPOSTOR" in self.role.upper():
            icon = "🎭"
            role_display = "IMPOSTOR"
        else:
            icon = "👨‍🚀"
            role_display = "CIVIL"
        
        # Título con icono
        self.title_label = ctk.CTkLabel(
            main_frame,
            text=f"{icon} {role_display} {icon}",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.color_style
        )
        self.title_label.pack(pady=(0, 10))
        
        # Texto del rol
        role_text = VisualRole.get_text(self.role)
        self.role_label = ctk.CTkLabel(
            main_frame,
            text=role_text,
            font=ctk.CTkFont(size=18),
            text_color=self.color_style
        )
        self.role_label.pack(pady=(0, 15))
        
        # Línea separadora
        separator = ctk.CTkFrame(main_frame, height=2, fg_color="#444444")
        separator.pack(fill="x", pady=10)
        
        # Contenido (palabra secreta para CIVILES)
        if self.word is not None:
            content_frame = ctk.CTkFrame(main_frame, fg_color="#1E1E1E", corner_radius=10)
            content_frame.pack(pady=15, fill="x")
            
            word_label = ctk.CTkLabel(
                content_frame,
                text="🔑 PALABRA SECRETA",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#FFD700"
            )
            word_label.pack(pady=(10, 5))
            
            secret_word = ctk.CTkLabel(
                content_frame,
                text=f'"{self.word}"',
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#00FF00"
            )
            secret_word.pack(pady=(0, 10))
        else:
            content_frame = ctk.CTkFrame(main_frame, fg_color="#1E1E1E", corner_radius=10)
            content_frame.pack(pady=15, fill="x")
            
            discover_label = ctk.CTkLabel(
                content_frame,
                text="❓",
                font=ctk.CTkFont(size=30),
                text_color="#FFD700"
            )
            discover_label.pack(pady=10)
            
            discover_text = ctk.CTkLabel(
                content_frame,
                text="No conoces la palabra secreta",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#FF4444"
            )
            discover_text.pack(pady=(0, 10))
        
        # Campo de texto para enviar palabra/descripción
        self._setup_word_input(main_frame)
        
        # Barra de progreso para el temporizador
        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            width=300,
            height=8,
            corner_radius=4
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(1.0)  # Iniciar en 100%
        
        # Texto del temporizador
        self.timer_label = ctk.CTkLabel(
            main_frame,
            text="Espera 5 segundos para enviar...",
            font=ctk.CTkFont(size=12),
            text_color="#FFD700"
        )
        self.timer_label.pack(pady=5)
        
        # Botón de enviar (inicialmente deshabilitado)
        self.send_button = ctk.CTkButton(
            main_frame,
            text="⏳ ESPERANDO",
            command=self._send_word,
            state="disabled",
            fg_color=self.bg_color,
            hover_color=self.color_style,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=200
        )
        self.send_button.pack(pady=15)
        
        # Instrucción adicional
        instruction_label = ctk.CTkLabel(
            main_frame,
            text=self.word_hint,
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            wraplength=450
        )
        instruction_label.pack(pady=5)
    
    def _setup_word_input(self, parent):
        """Configura el campo de entrada de palabra."""
        # Frame para el campo de texto
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(pady=15, fill="x")
        
        # Instrucción específica según el rol
        if "IMPOSTOR" in self.role.upper():
            label_text = "💬 Describe la palabra (crea una pista creíble):"
        else:
            label_text = "💬 Escribe tu descripción de la palabra secreta:"
        
        instruction = ctk.CTkLabel(
            input_frame,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#CCCCCC"
        )
        instruction.pack(anchor="w", pady=(0, 5))
        
        # Campo de texto obligatorio usando MandatoryField
        self.word_field = MandatoryField(
            master=input_frame,
            label=self.word_hint,
            expand=True,
            align="left",
            password=False,
            autofocus=True,
            callback=self._on_word_field_change
        )
        self.word_field.pack(fill="x", pady=(0, 5))
        
        # Contador de caracteres
        self.char_counter = ctk.CTkLabel(
            input_frame,
            text="0 / 100 caracteres",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        self.char_counter.pack(anchor="e")
        
        # Vincular evento para contar caracteres
        self.word_field.bind("<KeyRelease>", self._update_char_counter)
    
    def _update_char_counter(self, event=None):
        """Actualiza el contador de caracteres."""
        text = self.word_field.get()
        count = len(text)
        self.char_counter.configure(text=f"{count} / 100 caracteres")
        
        # Cambiar color si se acerca al límite
        if count > 90:
            self.char_counter.configure(text_color="#FF6600")
        elif count > 100:
            self.char_counter.configure(text_color="#FF0000")
        else:
            self.char_counter.configure(text_color="#666666")
    
    def _on_word_field_change(self):
        """Callback cuando el campo de palabra cambia."""
        # Verificar si el campo tiene contenido
        if self.word_field.is_unlocked and self.send_button.cget("state") == "normal":
            # Si el botón está desbloqueado y hay texto, se puede enviar
            pass
    
    def _start_unlock_timer(self):
        """Inicia el temporizador con barra de progreso."""
        def timer_thread():
            duration = 5
            
            for i in range(duration, 0, -1):
                if not self.running:
                    return
                
                # Actualizar barra de progreso (de 1.0 a 0.0)
                progress = i / duration
                self._update_progress(progress)
                self._update_timer(i)
                time.sleep(1)
            
            if self.running:
                self._unlock_button()
        
        threading.Thread(target=timer_thread, daemon=True).start()
    
    def _update_progress(self, value: float):
        """Actualiza la barra de progreso."""
        def update():
            if self.running and hasattr(self, 'progress_bar'):
                self.progress_bar.set(value)
        
        self.after(0, update)
    
    def _update_timer(self, seconds: int):
        """Actualiza el texto del temporizador."""
        def update():
            if self.running and hasattr(self, 'timer_label'):
                self.timer_label.configure(text=f"Puedes enviar en {seconds} segundos...")
        
        self.after(0, update)
    
    def _unlock_button(self):
        """Desbloquea el botón de enviar."""
        def unlock():
            if self.running and hasattr(self, 'send_button'):
                self.send_button.configure(
                    state="normal",
                    text="📤 ENVIAR PALABRA",
                    fg_color="#00AA00",
                    hover_color="#00CC00"
                )
                if hasattr(self, 'timer_label'):
                    self.timer_label.configure(
                        text="✓ ¡Ya puedes enviar tu palabra!",
                        text_color="#00FF00"
                    )
        
        self.after(0, unlock)
    
    def _send_word(self):
        """Envía la palabra al servidor y cierra el diálogo."""
        # Verificar que el campo tenga texto
        if not self.word_field.is_unlocked:
            self._show_error("Debes escribir una palabra o descripción antes de continuar.")
            return
        
        word_text = self.word_field.mandatory_value
        
        # Validar longitud mínima
        if len(word_text) < 3:
            self._show_error("La palabra/descripción debe tener al menos 3 caracteres.")
            return
        
        # Validar longitud máxima
        if len(word_text) > 100:
            self._show_error("La palabra/descripción no puede exceder los 100 caracteres.")
            return
        
        # Marcar que se envió la palabra
        self.word_sent = True
        
        # Llamar al callback con la palabra enviada
        if self.on_word_sent:
            self.on_word_sent(word_text)
        
        # Cerrar el diálogo
        self.running = False
        self.destroy()
    
    def _show_error(self, message: str):
        """Muestra un mensaje de error."""
        def show():
            error_label = ctk.CTkLabel(
                self,
                text=f"⚠️ {message}",
                font=ctk.CTkFont(size=12),
                text_color="#FF0000"
            )
            error_label.place(relx=0.5, rely=0.9, anchor="center")
            self.after(3000, error_label.destroy)
        
        self.after(0, show)
    
    def _on_close(self):
        """Maneja el cierre manual de la ventana."""
        if not self.word_sent:
            # Si se cierra sin enviar palabra, enviar una vacía o manejar error
            if self.on_word_sent:
                self.on_word_sent("")
        
        self.running = False
        self.destroy()