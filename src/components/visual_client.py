import flet as ft
from src.client.player_request import PlayerRequest
from src.components.role_display import RoleDisplay

from src.constants.const import CIVIL, IMPOSTOR


class VisualClient(ft.Container):
    def __init__(self, identifier: int, ip_address: str = None, port: int = None):
        super().__init__(content=   RoleDisplay(CIVIL, 'prueba'))
        self.__identifier: int = None
        self.__ip_address: str = None
        self.__port: int = None

        self.identifier: int = identifier
        self.ip_address: str = ip_address
        self.port: int = port

    @property
    def identifier(self) -> int:
        return self.__identifier
    
    @identifier.setter
    def identifier(self, identifier: int) -> None:
        if isinstance(identifier, int):
            self.__identifier = identifier

    @property
    def port(self) -> int:
        return self.__port
    
    @port.setter
    def port(self, port: int) -> None:
        if isinstance(port, int):
            self.__port = port

    @property
    def ip_address(self) -> str:
        return self.__ip_address
    
    @ip_address.setter
    def ip_address(self, ip_address: str) -> None:
        if isinstance(ip_address, str):
            self.__ip_address = ip_address    
