import socket
from src.constants.const import SERVER_IP, SERVER_PORT

class PlayerRequest(socket.socket):
    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.__connected: bool = None
        self.connected: bool = False

    def connect_to_server(self):
        try:
            self.connect((SERVER_IP, SERVER_PORT))
            self.connected = True

            while True:
                self.send(b"LOGIN:1234567890123456789012345678901234567890")
                data = self.recv(1024)
                print(data.decode())

            self.close()

        except Exception as e:
            print(f'Exception: {e}')

    @property
    def connected(self) -> bool:
        return self.__connected
    
    @connected.setter
    def connected(self, connected: bool) -> None:
        if isinstance(connected, bool):
            self.__connected = connected

    def close(self):
        self.connected = False
        self.close()

