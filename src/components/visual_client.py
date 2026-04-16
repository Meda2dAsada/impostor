import flet as ft
from src.client.player_request import PlayerRequest
from src.components.role_display import RoleDisplay
from src.components.username_input import UsernameInput

from src.constants.const import CIVIL, IMPOSTOR


class VisualClient(ft.Container):
    def __init__(self, identifier: int):
        super().__init__(content=UsernameInput())
        self.__identifier: int = None

        self.identifier: int = identifier
        self.player_request = PlayerRequest()
        self.player_request.connect_to_server()

    @property
    def identifier(self) -> int:
        return self.__identifier
    
    @identifier.setter
    def identifier(self, identifier: int) -> None:
        if isinstance(identifier, int):
            self.__identifier = identifier
