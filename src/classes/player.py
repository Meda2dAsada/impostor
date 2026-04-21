

class Player:
    def __init__(self, username: str, password: str, identifier: int = None, role: str = None):
        self.__username: str = None
        self.__password: str = None
        self.__identifier: int = None
        self.__role: str = None

        self.username: str = username
        self.password: str = password
        self.identifier: int = identifier
        self.role: str = role

    @property
    def identifier(self) -> int:
        return self.__identifier
    
    @identifier.setter
    def identifier(self, identifier: int) -> None:
        if isinstance(identifier, int):
            self.__identifier = identifier

    @property
    def username(self) -> str:
        return self.__username
    
    @username.setter
    def username(self, username: str) -> None:
        if isinstance(username, str):
            self.__username = username

    @property
    def password(self) -> str:
        return self.__password
    
    @password.setter
    def password(self, password: str) -> None:
        if isinstance(password, str):
            self.__password = password

    @property
    def role(self) -> str:
        return self.__role
    
    @role.setter
    def role(self, role: str) -> None:
        if isinstance(role, str):
            self.__role = role


