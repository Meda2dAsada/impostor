import customtkinter as ctk
from src.components.user_input import UserInput
from src.components.role_display import RoleDisplay
from src.components.voting_screen import VotingScreen
from src.classes.player import Player
from src.client.player_request import PlayerRequest
import threading


class VisualPlayer(ctk.CTkFrame):
    """
    Clase principal que maneja el flujo completo del juego.
    """
    
    def __init__(self, master):
        super().__init__(master)
        
        # Configurar el frame principal
        self.configure(fg_color="#2E1258")
        self.pack(fill="both", expand=True)
        
        # Variables de estado
        self.player = None
        self.player_request = None
        self.user_input = None
        self.waiting_screen = None
        self.ready_sent = False
        self.authenticated = False
        
        # Mostrar pantalla de login inicial
        self.show_login_screen()

        self.voting_screen = None
        self.current_phase = "waiting"  # waiting, role, voting, result

        # Nuevos métodos para manejar la votación


    def update_waiting_status(self, message: str, color: str = None, error: bool = False):
        """
        Actualiza el mensaje de estado con verificaciones de seguridad.
        """
        def update():
            try:
                # Verificar si el widget waiting_status existe y está vivo
                if hasattr(self, 'waiting_status') and self.waiting_status.winfo_exists():
                    self.waiting_status.configure(text=message)
                    if color:
                        self.waiting_status.configure(text_color=color)
                else:
                    # Si no existe, imprimir en consola como fallback
                    print(f"[STATUS] {message}")
                
                # Verificar si el log existe
                if hasattr(self, 'waiting_log') and self.waiting_log.winfo_exists():
                    self.waiting_log.configure(state="normal")
                    self.waiting_log.insert("end", f"{message}\n")
                    self.waiting_log.see("end")
                    self.waiting_log.configure(state="disabled")
            except Exception as e:
                # Ignorar errores de widgets destruidos
                print(f"Error al actualizar UI (ignorado): {e}")
        
        if threading.current_thread() is threading.main_thread():
            update()
        else:
            self.after(0, update)


    def show_voting_phase(self, chat_log: str, vote_req: str):
        """
        Muestra la fase de votación con los mensajes y botones.
        """
        def show():
            try:
                # Limpiar contenido actual
                self.clear_content()
                
                # Crear pantalla de votación
                self.voting_screen = VotingScreen(
                    self,
                    self.player.username if self.player else "Jugador",
                    on_vote_cast=self.on_vote_cast
                )
                
                # Mostrar los mensajes del chat
                num_players = self.voting_screen.display_messages(chat_log)
                
                # Habilitar votación con los IDs
                self.voting_screen.enable_voting(vote_req)
                
                # Actualizar estado (usar print si no hay waiting_status)
                print(f"📝 {num_players} jugadores han enviado sus descripciones")
                
            except Exception as e:
                print(f"Error al mostrar fase de votación: {e}")
        
        self.after(0, show)


    def on_vote_cast(self, player_id: int):
        """
        Callback cuando el jugador emite un voto.
        Envía el voto al servidor.
        """
        if self.player_request:
            self.player_request.send_vote(player_id)
            self.update_waiting_status(f"🗳️ Voto enviado al servidor (Jugador ID: {player_id})", "#FFD700")
            
            # Mostrar mensaje de espera por resultados
            self.show_waiting_screen("Esperando resultados de la votación...")


    def show_login_screen(self):
        """Muestra la pantalla de login (UserInput)."""
        self.clear_content()
        
        self.user_input = UserInput(
            self,
            on_submit=self.on_login_submit,
            on_cancel=self.on_login_cancel
        )
        self.user_input.pack(fill="both", expand=True)
    
    def on_login_submit(self, username: str, password: str):
        """Callback cuando el usuario envía sus credenciales."""
        # Crear objeto Player con las credenciales
        self.player = Player(username, password)
        
        # Crear PlayerRequest
        self.player_request = PlayerRequest(self.player)
        
        # Configurar callback para mensajes del servidor
        self.player_request.on_message_received = self.on_server_message
        
        # Mostrar pantalla de espera mientras se conecta
        self.show_waiting_screen("Conectando al servidor...")
        
        # Iniciar conexión en hilo separado
        self.connect_to_server()
    
    def on_login_cancel(self):
        """Callback cuando el usuario cancela el login."""
        print("Login cancelado")
    
    def connect_to_server(self):
        """Intenta conectar al servidor en un hilo separado."""
        def connect_thread():
            success = self.player_request.start_connection()
            
            if success:
                # Conexión exitosa y autenticación OK
                self.authenticated = True
                self.update_waiting_status(
                    "✓ Autenticación exitosa",
                    "#00FF00"
                )
                # El servidor ahora espera READY
                self.update_waiting_status(
                    "Esperando inicio del juego...",
                    "#FFD700"
                )
                # Agregar botón para enviar READY manualmente
                self.add_ready_button()
            else:
                # Error de conexión o autenticación
                self.update_waiting_status(
                    "Error de autenticación. Verifica tus credenciales.",
                    "#FF0000",
                    error=True
                )
                self.show_login_retry_button()
        
        threading.Thread(target=connect_thread, daemon=True).start()

    def on_server_message(self, message: str):
        """
        Procesa los mensajes del servidor.
        """

        def process():
            print(f"Mensaje del servidor: {message}")

            # Fase de CHAT_LOG (mensajes de todos los jugadores)
            if message.startswith("CHAT_LOG:"):
                # Guardar el chat log completo
                self.chat_log = message

            # Fase de VOTACIÓN - Lista de jugadores para votar
            elif message.startswith("VOTE_REQ:"):
                if hasattr(self, 'chat_log'):
                    self.show_voting_phase(self.chat_log, message)
                else:
                    print("Error: CHAT_LOG no recibido antes de VOTE_REQ")

            # Fase de RESULTADO
            elif message.startswith("RESULTADO:"):
                self.handle_game_result(message)

            # Rol y otros mensajes
            elif message.startswith("ROLE:"):
                self.handle_role_message(message)

            elif message.startswith("ERROR:"):
                self.handle_error_message(message)

        # Solo UNA llamada
        self.after(0, process)
        # ELIMINA la línea duplicada: self.after(0, process)
    def handle_role_message(self, message: str):
        """
        Maneja el mensaje de rol y muestra el diálogo para enviar palabra.
        """
        role_text = message[5:] if len(message) > 5 else ""
        
        # Extraer el rol y la palabra
        if "IMPOSTOR" in role_text:
            role = "IMPOSTOR"
            word = None
        else:
            import re
            match = re.search(r'\[(.*?)\]', role_text)
            word = match.group(1) if match else None
            role = "CIVIL"
        
        # Mostrar diálogo de rol y enviar palabra
        def on_word_sent(word_text: str):
            if self.player_request:
                self.player_request.send_word(word_text)
                self.update_waiting_status("✓ Palabra enviada. Esperando a otros jugadores...", "#00FF00")
            
            # Mostrar pantalla de espera mientras todos envían sus palabras
            self.show_waiting_screen("Esperando a que todos los jugadores envíen sus descripciones...")
        
        def show():
            role_dialog = RoleDisplay(self, role, word, on_word_sent=on_word_sent)
            self.wait_window(role_dialog)
        
        self.after(0, show)    
    def add_ready_button(self):
        """Agrega un botón para que el jugador envíe READY manualmente."""
        def add():
            if hasattr(self, 'waiting_center_frame'):
                # Verificar si ya existe el botón
                for child in self.waiting_center_frame.winfo_children():
                    if isinstance(child, ctk.CTkButton) and "Listo" in child.cget("text"):
                        return
                
                ready_button = ctk.CTkButton(
                    self.waiting_center_frame,
                    text="✓ ESTOY LISTO",
                    command=self.send_ready_command,
                    fg_color="#00AA00",
                    hover_color="#00CC00",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    height=40,
                    width=200
                )
                ready_button.pack(pady=20)
                
                # Instrucción
                instruction = ctk.CTkLabel(
                    self.waiting_center_frame,
                    text="Presiona 'Estoy Listo' cuando estés preparado para jugar",
                    font=ctk.CTkFont(size=12),
                    text_color="#FFD700"
                )
                instruction.pack(pady=5)
        
        self.after(0, add)
    
    def send_ready_command(self):
        """Envía el comando READY al servidor."""
        if not self.ready_sent and self.player_request:
            self.ready_sent = True
            success = self.player_request.send_ready()
            
            if success:
                self.update_waiting_status(
                    "✓ Listo confirmado. Esperando a otros jugadores...",
                    "#00FF00"
                )
                # Deshabilitar el botón de ready
                self.disable_ready_button()
                # Agregar indicador de espera
                self.add_waiting_indicator()
            else:
                self.update_waiting_status(
                    "✗ Error al enviar confirmación",
                    "#FF0000",
                    error=True
                )
                self.ready_sent = False
    
    def disable_ready_button(self):
        """Deshabilita el botón de ready después de enviarlo."""
        def disable():
            if hasattr(self, 'waiting_center_frame'):
                for child in self.waiting_center_frame.winfo_children():
                    if isinstance(child, ctk.CTkButton) and "Listo" in child.cget("text"):
                        child.configure(state="disabled", text="✓ LISTO ENVIADO", fg_color="#555555")
                        break
        
        self.after(0, disable)


    def show_waiting_screen(self, message: str):
        """Muestra la pantalla de espera de forma segura."""
        def create():
            try:
                # Limpiar contenido actual
                self.clear_content()
                
                # Crear nuevo frame
                self.waiting_screen = ctk.CTkFrame(self, fg_color="#2E1258")
                self.waiting_screen.pack(fill="both", expand=True)
                
                # Frame central
                self.waiting_center_frame = ctk.CTkFrame(self.waiting_screen, fg_color="transparent")
                self.waiting_center_frame.pack(expand=True)
                
                # Título
                self.waiting_title = ctk.CTkLabel(
                    self.waiting_center_frame,
                    text="Conectando al servidor",
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color="#FFD700"
                )
                self.waiting_title.pack(pady=(0, 20))
                
                # Progress bar
                self.waiting_progress = ctk.CTkProgressBar(
                    self.waiting_center_frame,
                    width=300,
                    mode="indeterminate"
                )
                self.waiting_progress.pack(pady=10)
                self.waiting_progress.start()
                
                # Mensaje de estado
                self.waiting_status = ctk.CTkLabel(
                    self.waiting_center_frame,
                    text=message,
                    font=ctk.CTkFont(size=14),
                    text_color="#CCCCCC"
                )
                self.waiting_status.pack(pady=10)
                
                # Área de logs (opcional)
                self.waiting_log = ctk.CTkTextbox(
                    self.waiting_center_frame,
                    width=500,
                    height=200,
                    fg_color="#1E1E1E",
                    text_color="#FFFFFF",
                    font=ctk.CTkFont(size=11)
                )
                self.waiting_log.pack(pady=20)
                self.waiting_log.insert("0.0", "=== CONEXIÓN CON EL SERVIDOR ===\n")
                self.waiting_log.configure(state="disabled")
                
            except Exception as e:
                print(f"Error al crear pantalla de espera: {e}")
        
        self.after(0, create)

    def stop_progress_indicator(self):
        """Detiene el indicador de progreso."""
        def stop():
            if hasattr(self, 'waiting_progress'):
                self.waiting_progress.stop()
                self.waiting_progress.pack_forget()
        
        self.after(0, stop)
    
    def add_waiting_indicator(self):
        """Agrega un indicador de que se está esperando."""
        def add():
            if hasattr(self, 'waiting_center_frame'):
                waiting_label = ctk.CTkLabel(
                    self.waiting_center_frame,
                    text="⏳ Esperando a otros jugadores para iniciar...",
                    font=ctk.CTkFont(size=12),
                    text_color="#FFD700"
                )
                waiting_label.pack(pady=5)
        
        self.after(0, add)
    
    def show_role_message(self, message: str, color: str):
        """Muestra el mensaje del rol."""
        def show():
            if hasattr(self, 'waiting_title'):
                self.waiting_title.configure(text=message, text_color=color)
        
        self.after(0, show)
    
    def show_login_retry_button(self):
        """Muestra botón para volver al login."""
        def add():
            if hasattr(self, 'waiting_center_frame'):
                retry_btn = ctk.CTkButton(
                    self.waiting_center_frame,
                    text="Volver al inicio de sesión",
                    command=self.return_to_login,
                    fg_color="#FF8000",
                    hover_color="#FF6600"
                )
                retry_btn.pack(pady=10)
        
        self.after(0, add)
    
    def show_play_again_button(self):
        """Muestra botón para jugar de nuevo."""
        def add():
            if hasattr(self, 'waiting_center_frame'):
                play_again_btn = ctk.CTkButton(
                    self.waiting_center_frame,
                    text="Jugar de nuevo",
                    command=self.reset_and_play_again,
                    fg_color="#00AA00",
                    hover_color="#00CC00"
                )
                play_again_btn.pack(pady=10)
        
        self.after(0, add)
    
    def handle_chat_log(self, message: str):
        """Maneja el historial de chat."""
        self.update_waiting_status("📝 Historial de chat recibido", "#888888")
        # Aquí puedes procesar el historial del chat
    
    def handle_vote_request(self, message: str):
        """Maneja la solicitud de voto."""
        self.update_waiting_status("🗳️ Fase de votación iniciada", "#FFD700")
        # Aquí puedes mostrar la interfaz de votación
        print(f"Solicitud de voto: {message}")
    
    def return_to_login(self):
        """Vuelve al login."""
        self.ready_sent = False
        self.authenticated = False
        if self.player_request:
            try:
                self.player_request.close_connection()
            except:
                pass
        self.clear_content()
        self.show_login_screen()
    
    def reset_and_play_again(self):
        """Reinicia el juego."""
        self.return_to_login()
    
    def clear_content(self):
        """Limpia todo el contenido y las referencias."""
        # Limpiar referencias a widgets antiguos
        self.waiting_screen = None
        self.waiting_center_frame = None
        self.waiting_title = None
        self.waiting_progress = None
        self.waiting_status = None
        self.waiting_log = None
        self.voting_screen = None
        
        # Destruir todos los widgets hijos
        for widget in self.winfo_children():
            try:
                widget.destroy()
            except:
                pass

    def show_role_display(self, role: str, word: str = None):
        """
        Muestra el diálogo de rol con envío de palabra.
        """
        def on_word_sent(word_text: str):
            # Enviar la palabra al servidor
            if self.player_request:
                self.player_request.send_word(word_text)
                self.update_waiting_status(f"✓ Palabra enviada: {word_text[:50]}...", "#00FF00")
            
            # Continuar con la siguiente fase
            self.continue_after_role()
        
        def show():
            role_dialog = RoleDisplay(self, role, word, on_word_sent=on_word_sent)
            # Esperar a que se cierre el diálogo
            self.wait_window(role_dialog)
        
        self.after(0, show)

    def continue_after_role(self):
        """Continúa el juego después de enviar la palabra."""
        self.update_waiting_status("Esperando a que todos los jugadores envíen su palabra...")
        # El servidor ahora esperará a que todos envíen su WORD


    def continue_after_role(self):
        """Continúa el juego después de mostrar el rol."""
        self.update_waiting_status("Rol confirmado. Continuando...")
        # Aquí puedes continuar con la siguiente fase del juego


    def handle_game_result(self, message: str):
        """
        Maneja el resultado del juego enviado por el servidor.
        """
        # Extraer el mensaje de resultado
        if message.startswith("RESULTADO:"):
            result_message = message[10:] if len(message) > 10 else message
        else:
            result_message = message
        
        # Mostrar diálogo de resultado
        self.show_result_dialog(result_message)

    def show_result_dialog(self, result_message: str):
        """
        Muestra un diálogo con el resultado del juego.
        """
        def show():
            # Crear ventana de resultado
            result_window = ctk.CTkToplevel(self)
            result_window.title("🎮 Resultado del Juego")
            result_window.configure(fg_color="#2E1258")
            result_window.geometry("500x350")
            result_window.resizable(False, False)
            
            # Hacer modal
            result_window.transient(self)
            result_window.grab_set()
            
            # Frame principal
            main_frame = ctk.CTkFrame(result_window, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=30, pady=30)
            
            # Determinar icono y color según el resultado
            if "Civiles" in result_message or "civiles" in result_message:
                icon = "🎉"
                color = "#00FF00"
                title_text = "¡VICTORIA DE LOS CIVILES!"
            elif "Impostor" in result_message or "impostor" in result_message:
                icon = "😈"
                color = "#FF4444"
                title_text = "VICTORIA DEL IMPOSTOR"
            else:
                icon = "🎮"
                color = "#FFD700"
                title_text = "FIN DEL JUEGO"
            
            # Título
            title_label = ctk.CTkLabel(
                main_frame,
                text=f"{icon} {title_text} {icon}",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color
            )
            title_label.pack(pady=(0, 20))
            
            # Línea decorativa
            separator = ctk.CTkFrame(main_frame, height=2, fg_color=color)
            separator.pack(fill="x", pady=10)
            
            # Mensaje de resultado
            result_label = ctk.CTkLabel(
                main_frame,
                text=result_message,
                font=ctk.CTkFont(size=16),
                text_color="#FFFFFF",
                wraplength=400,
                justify="center"
            )
            result_label.pack(pady=30)
            
            # Botones
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(pady=20)
            
            # Botón de jugar de nuevo
            play_again_btn = ctk.CTkButton(
                button_frame,
                text="🎮 Jugar de nuevo",
                command=lambda: self._restart_game(result_window),
                fg_color="#00AA00",
                hover_color="#00CC00",
                font=ctk.CTkFont(size=14, weight="bold"),
                height=40,
                width=180
            )
            play_again_btn.pack(side="left", padx=10)
            
            # Botón de salir
            exit_btn = ctk.CTkButton(
                button_frame,
                text="🚪 Salir",
                command=lambda: self._exit_game(result_window),
                fg_color="#AA0000",
                hover_color="#CC0000",
                font=ctk.CTkFont(size=14, weight="bold"),
                height=40,
                width=180
            )
            exit_btn.pack(side="left", padx=10)
        
        self.after(0, show)

    def _restart_game(self, result_window):
        """
        Reinicia el juego cerrando el resultado y volviendo al login.
        """
        try:
            result_window.destroy()
        except:
            pass
        
        # Cerrar conexión actual
        if self.player_request:
            try:
                self.player_request.close_connection()
            except:
                pass
        
        # Resetear estado
        self.ready_sent = False
        self.authenticated = False
        self.current_phase = "waiting"
        
        # Limpiar y volver al login
        self.clear_content()
        self.show_login_screen()

    def _exit_game(self, result_window):
        """
        Sale del juego cerrando la aplicación.
        """
        try:
            # Cerrar conexión
            if self.player_request:
                try:
                    self.player_request.close_connection()
                except:
                    pass
            
            # Cerrar la ventana principal
            result_window.destroy()
            
            # Buscar y cerrar la ventana raíz
            root = self.winfo_toplevel()
            root.quit()
            root.destroy()
        except:
            pass