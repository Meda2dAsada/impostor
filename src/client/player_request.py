import socket
import threading
from src.classes.player import Player
from src.constants.const import SERVER_IP, SERVER_PORT

class PlayerRequest(socket.socket):
    def __init__(self, player: Player):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.__player = player
        self.__connected = False
        self.on_message_received = None 

    def start_connection(self):
        try:
            self.connect((SERVER_IP, SERVER_PORT))
            self.__connected = True
            
            # El servidor C espera LOGIN:usuario:password inmediatamente
            login_msg = f"LOGIN:{self.__player.username}:{self.__player.password}"
            self.send(login_msg.encode())
            
            # Esperar respuesta de autenticación
            response = self.recv(1024).decode('utf-8')
            print(f"Respuesta del servidor: {response}")
            
            # Si la autenticación es exitosa, iniciar hilo de escucha
            if response.startswith("OK:"):
                # Hilo de escucha para recibir ROLES, CHAT_LOG, etc.
                threading.Thread(target=self.__listen_loop, daemon=True).start()
                return True
            else:
                # Si hay error, notificar al callback
                if self.on_message_received:
                    self.on_message_received(response)
                return False
                
        except Exception as e:
            print(f"Error conexión: {e}")
            if self.on_message_received:
                self.on_message_received(f"ERROR:Conexión fallida: {e}")
            return False
    
    def send_ready(self):
        """Envía el comando READY al servidor."""
        if self.__connected:
            try:
                self.send("READY".encode())
                print("READY enviado al servidor")
                return True
            except Exception as e:
                print(f"Error enviando READY: {e}")
                return False
        return False
    
    def send_word(self, word: str):
        """Envía una palabra al servidor (fase de chat)."""
        if self.__connected:
            try:
                self.send(f"WORD:{word}".encode())
                return True
            except Exception as e:
                print(f"Error enviando WORD: {e}")
                return False
        return False
    
    def send_vote(self, vote_id: int):
        """Envía un voto al servidor."""
        if self.__connected:
            try:
                self.send(f"VOTE:{vote_id}".encode())
                return True
            except Exception as e:
                print(f"Error enviando VOTE: {e}")
                return False
        return False
    
    def send_command(self, command: str):
        """Método genérico para enviar comandos."""
        if self.__connected:
            try:
                self.send(command.encode())
                return True
            except Exception as e:
                print(f"Error enviando {command}: {e}")
                return False
        return False
    
    def __listen_loop(self):
        """Bucle de escucha para mensajes del servidor."""
        while self.__connected:
            try:
                data = self.recv(2048).decode('utf-8')
                if not data:
                    break
                
                print(f"Mensaje recibido del servidor: {data}")
                
                if self.on_message_received:
                    # Llamar directamente al callback
                    self.on_message_received(data)
            except Exception as e:
                print(f"Error en bucle de escucha: {e}")
                break
        
        self.__connected = False
    
    def close_connection(self):
        """Cierra la conexión."""
        self.__connected = False
        try:
            self.close()
        except:
            pass