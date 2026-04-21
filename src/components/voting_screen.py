import customtkinter as ctk
from src.components.mandatory_button import MandatoryButton
import threading

class VotingScreen(ctk.CTkFrame):
    def __init__(self, master, player_name: str, on_vote_cast=None):
        super().__init__(master)
        
        self.player_name = player_name
        self.on_vote_cast = on_vote_cast
        self.has_voted = False
        self.players_data = []
        self.vote_buttons = {}
        
        # Configurar frame
        try:
            self.configure(fg_color="#2E1258")
            self.pack(fill="both", expand=True)
            self._setup_ui()
        except Exception as e:
            print(f"Error en VotingScreen: {e}")
    
    def _setup_ui(self):
        """Configura la interfaz de votación."""
        try:
            title_label = ctk.CTkLabel(
                self,
                text="🗳️ FASE DE VOTACIÓN 🗳️",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#FFD700"
            )
            title_label.pack(pady=(20, 10))
            
            # Subtítulo
            subtitle = ctk.CTkLabel(
                self,
                text="Lee las descripciones y vota por el jugador que creas que es el IMPOSTOR",
                font=ctk.CTkFont(size=14),
                text_color="#CCCCCC"
            )
            subtitle.pack(pady=(0, 20))
            
            # Área scrollable para los mensajes de los jugadores
            self.scrollable_frame = ctk.CTkScrollableFrame(
                self,
                fg_color="#1E1E1E",
                corner_radius=10,
                border_width=0
            )
            self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Frame para los botones de votación (se mostrará después)
            self.vote_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.vote_frame.pack(fill="x", padx=20, pady=10)

            pass
        except Exception as e:
            print(f"Error en _setup_ui: {e}")

    
    def display_messages(self, chat_log: str):
        """
        Procesa el CHAT_LOG del servidor y muestra los mensajes.
        El formato esperado: "CHAT_LOG:\n[Player1]: mensaje1\n[Player2]: mensaje2\n"
        """
        # Limpiar frame existente
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.players_data = []
        
        # Procesar el chat log
        lines = chat_log.strip().split('\n')
        for line in lines:
            if line.startswith('CHAT_LOG:'):
                continue
            
            # Formato esperado: "[Nombre]: mensaje"
            if ']:' in line:
                # Extraer nombre y mensaje
                bracket_pos = line.find(']')
                if bracket_pos > 0:
                    nombre = line[1:bracket_pos]  # Quitar el '['
                    mensaje = line[bracket_pos + 2:]  # Quitar ']: '
                    
                    # Buscar el ID del jugador (lo asignaremos después con VOTE_REQ)
                    self.players_data.append({
                        'nombre': nombre,
                        'mensaje': mensaje,
                        'id': -1  # ID temporal, se actualizará con VOTE_REQ
                    })
                    
                    # Crear frame para cada mensaje
                    self._create_message_card(nombre, mensaje)
        
        # Actualizar IDs cuando llegue VOTE_REQ
        return len(self.players_data)
    
    def _create_message_card(self, player_name: str, message: str):
        """
        Crea una tarjeta visual para cada mensaje de jugador.
        """
        # Frame contenedor de la tarjeta
        card_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="#2D2D2D",
            corner_radius=10,
            border_width=1,
            border_color="#444444"
        )
        card_frame.pack(fill="x", pady=5, padx=10)
        
        # Cabecera con el nombre del jugador
        name_label = ctk.CTkLabel(
            card_frame,
            text=f"👤 {player_name}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#7357FF"
        )
        name_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Separador
        separator = ctk.CTkFrame(card_frame, height=1, fg_color="#444444")
        separator.pack(fill="x", padx=10)
        
        # Mensaje
        message_label = ctk.CTkLabel(
            card_frame,
            text=f'"{message}"',
            font=ctk.CTkFont(size=13),
            text_color="#FFFFFF",
            wraplength=450,
            justify="left"
        )
        message_label.pack(anchor="w", padx=15, pady=(10, 10))
        
        # Botón de voto (se habilitará después de mostrar todos los mensajes)
        vote_btn = ctk.CTkButton(
            card_frame,
            text="🗳️ Votar por este jugador",
            command=lambda p=player_name: self._prepare_vote(p),
            state="disabled",
            fg_color="#444444",
            hover_color="#7357FF",
            height=30,
            width=150
        )
        vote_btn.pack(anchor="e", padx=15, pady=(0, 10))
        
        # Guardar referencia al botón
        if not hasattr(self, 'vote_buttons'):
            self.vote_buttons = {}
        self.vote_buttons[player_name] = vote_btn
    
    def enable_voting(self, players_list: str):
        """
        Habilita los botones de votación con los IDs correctos.
        Formato esperado: "VOTE_REQ:0-Jugador1,1-Jugador2,2-Jugador3,"
        """
        # Procesar la lista de jugadores con IDs
        if players_list.startswith("VOTE_REQ:"):
            players_part = players_list[9:]  # Quitar "VOTE_REQ:"
            
            # Parsear "0-Jugador1,1-Jugador2,2-Jugador3,"
            for item in players_part.split(','):
                if '-' in item:
                    parts = item.split('-')
                    if len(parts) == 2:
                        player_id = int(parts[0])
                        player_name = parts[1]
                        
                        # Actualizar ID en players_data
                        for player in self.players_data:
                            if player['nombre'] == player_name:
                                player['id'] = player_id
                                break
        
        # Habilitar botones de voto
        for player_name, button in self.vote_buttons.items():
            # Encontrar el ID del jugador
            player_id = None
            for player in self.players_data:
                if player['nombre'] == player_name:
                    player_id = player['id']
                    break
            
            if player_id is not None and player_id >= 0:
                # Configurar el comando con el ID correcto
                button.configure(
                    state="normal",
                    command=lambda pid=player_id, pname=player_name: self._cast_vote(pid, pname),
                    fg_color="#00AA00",
                    hover_color="#00CC00"
                )
        
        # Mostrar instrucciones de votación
        self._show_voting_instructions()
    
    def _prepare_vote(self, player_name: str):
        """
        Prepara la votación (método legacy, mantener por compatibilidad).
        """
        # Encontrar el ID del jugador
        for player in self.players_data:
            if player['nombre'] == player_name:
                self._cast_vote(player['id'], player_name)
                break
    
    def _cast_vote(self, player_id: int, player_name: str):
        """
        Emite un voto por un jugador.
        """
        if self.has_voted:
            self._show_message("⚠️ Ya has emitido tu voto", "#FF6600")
            return
        
        if player_id < 0:
            self._show_message("❌ Error: No se pudo identificar al jugador", "#FF0000")
            return
        
        # Marcar como votado
        self.has_voted = True
        
        # Deshabilitar todos los botones
        for button in self.vote_buttons.values():
            button.configure(state="disabled")
        
        # Mostrar confirmación
        self._show_message(f"✓ Votaste por: {player_name}", "#00FF00")
        
        # Llamar al callback con el ID del votado
        if self.on_vote_cast:
            self.on_vote_cast(player_id)
    
    def _show_voting_instructions(self):
        """Muestra instrucciones para votar."""
        instruction_frame = ctk.CTkFrame(self.vote_frame, fg_color="#1E1E1E", corner_radius=8)
        instruction_frame.pack(fill="x", pady=5)
        
        instruction_text = ctk.CTkLabel(
            instruction_frame,
            text="💡 Haz clic en 'Votar por este jugador' debajo del mensaje que te parezca más sospechoso\nSolo puedes votar una vez",
            font=ctk.CTkFont(size=12),
            text_color="#FFD700",
            justify="center"
        )
        instruction_text.pack(pady=10)
    
    def _show_message(self, message: str, color: str):
        """Muestra un mensaje temporal."""
        msg_label = ctk.CTkLabel(
            self.vote_frame,
            text=message,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=color
        )
        msg_label.pack(pady=5)
        self.after(3000, msg_label.destroy)
    
    def reset(self):
        """Resetea el estado de votación."""
        self.has_voted = False
        self.players_data = []
        if hasattr(self, 'vote_buttons'):
            self.vote_buttons.clear()