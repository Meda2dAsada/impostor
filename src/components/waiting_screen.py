import customtkinter as ctk
from src.client.player_request import PlayerRequest
import threading


class WaitingScreen(ctk.CTkFrame):
    """
    Pantalla de espera que se conecta al servidor y espera respuestas.
    Muestra el estado de la conexión y los mensajes del servidor.
    """
    
    def __init__(self, master, player_request: PlayerRequest, on_game_start=None):
        super().__init__(master)
        
        self.player_request = player_request
        self.on_game_start = on_game_start  # Callback cuando el juego comienza
        self._connected = False
        
        # Configurar el frame
        self.configure(fg_color="#2E1258")
        self.pack(fill="both", expand=True)
        
        # Crear UI
        self._setup_ui()
        
        # Iniciar conexión en un hilo separado
        self._start_connection()
    
    def _setup_ui(self):
        """Configura la interfaz de la pantalla de espera."""
        # Frame central para centrar contenido
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True)
        
        # Título
        self.title_label = ctk.CTkLabel(
            center_frame,
            text="Conectando al servidor...",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FFD700"  # Amarillo
        )
        self.title_label.pack(pady=(0, 20))
        
        # Indicador de carga (spinner)
        self.progressbar = ctk.CTkProgressBar(
            center_frame,
            width=300,
            height=10,
            mode="indeterminate"  # Modo indeterminado para mostrar actividad
        )
        self.progressbar.pack(pady=10)
        self.progressbar.start()  # Iniciar animación
        
        # Label de estado
        self.status_label = ctk.CTkLabel(
            center_frame,
            text="Estableciendo conexión...",
            font=ctk.CTkFont(size=14),
            text_color="#CCCCCC"
        )
        self.status_label.pack(pady=10)
        
        # Área de mensajes del servidor (opcional, para debug)
        self.messages_text = ctk.CTkTextbox(
            center_frame,
            width=400,
            height=150,
            fg_color="#1E1E1E",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12)
        )
        self.messages_text.pack(pady=20)
        self.messages_text.insert("0.0", "Esperando respuestas del servidor...\n")
        self.messages_text.configure(state="disabled")  # Solo lectura
    
    def _start_connection(self):
        """Inicia la conexión al servidor en un hilo separado."""
        def connect_thread():
            # Conectar al servidor
            success = self.player_request.start_connection()
            
            if success:
                self._connected = True
                # Actualizar UI desde el hilo principal
                self._update_ui_safe(
                    "¡Conectado al servidor! Esperando asignación de rol...",
                    "#00FF00"
                )
                
                # Configurar callback para mensajes recibidos
                self.player_request.on_message_received = self._on_server_message
            else:
                self._update_ui_safe(
                    "Error de conexión al servidor",
                    "#FF0000",
                    error=True
                )
        
        # Iniciar hilo de conexión
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def _update_ui_safe(self, message: str, color: str = None, error: bool = False):
        """Actualiza la UI de forma segura desde cualquier hilo."""
        def update():
            self.status_label.configure(text=message)
            if color:
                self.status_label.configure(text_color=color)
            
            # Agregar al área de mensajes
            self.messages_text.configure(state="normal")
            self.messages_text.insert("end", f"{message}\n")
            self.messages_text.see("end")  # Scroll al final
            self.messages_text.configure(state="disabled")
            
            if error:
                # Detener el progreso si hay error
                self.progressbar.stop()
                self.progressbar.pack_forget()
                
                # Agregar botón de reintentar
                self._add_retry_button()
        
        # Ejecutar en el hilo principal
        if threading.current_thread() is threading.main_thread():
            update()
        else:
            self.after(0, update)
    
    def _add_retry_button(self):
        """Agrega un botón para reintentar la conexión."""
        retry_button = ctk.CTkButton(
            self.winfo_children()[0],  # center_frame
            text="Reintentar conexión",
            command=self._retry_connection,
            fg_color="#FF8000",
            hover_color="#FF6600"
        )
        retry_button.pack(pady=10)
    
    def _retry_connection(self):
        """Reintenta la conexión al servidor."""
        # Limpiar UI actual
        for widget in self.winfo_children():
            widget.destroy()
        
        # Reconfigurar UI
        self._setup_ui()
        
        # Reiniciar conexión
        self._start_connection()
    
    def _on_server_message(self, message: str):
        """
        Callback que se ejecuta cuando el servidor envía un mensaje.
        Este método es llamado desde el hilo de escucha.
        """
        def process_message():
            self.messages_text.configure(state="normal")
            self.messages_text.insert("end", f"Servidor: {message}\n")
            self.messages_text.see("end")
            self.messages_text.configure(state="disabled")
            
            # Procesar diferentes tipos de mensajes
            if message.startswith("ROLE:"):
                # El servidor asigna un rol (IMPOSTOR o CREW)
                role = message.split(":")[1]
                self._handle_role_assignment(role)
                
            elif message.startswith("CHAT_LOG:"):
                # Recibir historial de chat (opcional)
                chat_content = message[9:]  # Quitar "CHAT_LOG:"
                self._handle_chat_log(chat_content)
                
            elif message.startswith("START_GAME"):
                # El juego comienza
                self._handle_game_start()
                
            elif message.startswith("ERROR:"):
                # Error del servidor
                error_msg = message[6:]
                self._handle_error(error_msg)
            
            elif message.startswith("PLAYERS:"):
                # Lista de jugadores conectados
                players = message[8:].split(",")
                self._handle_players_list(players)
        
        # Ejecutar en el hilo principal
        self.after(0, process_message)
    
    def _handle_role_assignment(self, role: str):
        """Maneja la asignación de rol por parte del servidor."""
        self.title_label.configure(text=f"¡Eres {role}!")
        
        if role == "IMPOSTOR":
            self.status_label.configure(
                text="Eres el Impostor. ¡Elimina a la tripulación sin ser descubierto!",
                text_color="#FF4444"
            )
        else:
            self.status_label.configure(
                text="Eres Civil. Completa tareas y descubre al Impostor.",
                text_color="#44FF44"
            )
        
        # Detener el progreso
        self.progressbar.stop()
        self.progressbar.pack_forget()
        
        # Agregar botón de "Listo" para iniciar el juego
        self._add_ready_button()
    
    def _add_ready_button(self):
        """Agrega un botón para indicar que el jugador está listo."""
        ready_button = ctk.CTkButton(
            self.winfo_children()[0],  # center_frame
            text="¡Listo para jugar!",
            command=self._send_ready,
            fg_color="#00AA00",
            hover_color="#00CC00",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        ready_button.pack(pady=20)
    
    def _send_ready(self):
        """Envía el comando READY al servidor."""
        self.player_request.send_command("READY")
        self.status_label.configure(text="Esperando a que otros jugadores estén listos...")
        
        # Deshabilitar el botón
        for widget in self.winfo_children()[0].winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "¡Listo para jugar!":
                widget.configure(state="disabled", text="¡Listo! Esperando...")
                break
    
    def _handle_game_start(self):
        """Maneja el inicio del juego."""
        self.status_label.configure(text="¡El juego comienza!")
        
        # Llamar al callback si existe
        if self.on_game_start:
            # Ejecutar en el hilo principal
            self.after(0, lambda: self.on_game_start(self))
    
    def _handle_chat_log(self, chat_content: str):
        """Maneja el historial de chat recibido."""
        # Esto puede ser usado para cargar mensajes anteriores
        pass
    
    def _handle_error(self, error_msg: str):
        """Maneja errores del servidor."""
        self.status_label.configure(
            text=f"Error del servidor: {error_msg}",
            text_color="#FF0000"
        )
        self._add_retry_button()
    
    def _handle_players_list(self, players: list):
        """Muestra la lista de jugadores conectados."""
        players_text = "Jugadores conectados: " + ", ".join(players)
        self.messages_text.configure(state="normal")
        self.messages_text.insert("end", f"{players_text}\n")
        self.messages_text.see("end")
        self.messages_text.configure(state="disabled")
    
    def send_chat_message(self, message: str):
        """Envía un mensaje de chat al servidor."""
        if self._connected and message.strip():
            self.player_request.send_command(f"CHAT:{message}")
    
    def send_vote(self, target_player: str):
        """Envía un voto para eliminar a un jugador."""
        if self._connected:
            self.player_request.send_command(f"VOTE:{target_player}")
    
    def send_word(self, word: str):
        """Envía una palabra (para el modo de juego específico)."""
        if self._connected:
            self.player_request.send_command(f"WORD:{word}")
    
    def destroy(self):
        """Limpia la conexión al cerrar la pantalla."""
        self._connected = False
        try:
            self.player_request.close()
        except:
            pass
        super().destroy()