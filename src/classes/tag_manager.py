from enum import Enum


class TagManager(Enum):
    LOGIN: str = 'LOGIN:'
    IDENTIFIER: str = 'IDENTIFIER:'
    ROLE: str = 'ROLE:'

    @staticmethod
    def login(username: str, password: str) -> str:
        return f'{TagManager.LOGIN}{username}:{password}'
    
    @staticmethod
    def identifier(identifier: int) -> str:
        return f'{TagManager.IDENTIFIER}{identifier}'
    
    @staticmethod
    def role(role: str) -> str:
        return f'{TagManager.ROLE}{role}'
    

    def players(self):pass