
CIVIL: str = 'CIVIL'
IMPOSTOR: str = 'IMPOSTOR'

SERVER_IP: str = 'localhost'
SERVER_PORT: int = 5000

class MandatoryButtonColors:
    BG_COLOR: str = '#4d185a'
    OVERLAY: str = '#5c1c6b'
    COLOR: str = '#00cc00'


class MandatoryFieldColors:
    LABEL: str = '#00ddbd'
    LOCKED: str = '#FF0000'
    WAITING: str = '#FF8000'
    UNLOCKED: str = '#00FF00'

class VisualRole:
    ROLE_COLORS: dict[str, str]= {CIVIL: '#00F5D4', IMPOSTOR: '#FF006E'}
    ROLE_BGCOLORS: dict[str, str] = {CIVIL: '#006254', IMPOSTOR: '#66002c'}
    ROLE_TEXT: dict[str, str] = {CIVIL: 'Eres civil. Que el impostor no te engañe.', IMPOSTOR: 'Eres impostor. Debes engañar a los demás.'}
    ROLE_WORD_HINT: dict[str, str] = {CIVIL: 'Escribe una palabra asociada a la palabra secreta.', IMPOSTOR: 'Escribe una palabra para intentar no ser descubierto.'}

    @staticmethod
    def get_color(role: str):
        return VisualRole.ROLE_COLORS.get(role)

    @staticmethod
    def get_bgcolor(role: str):
        return VisualRole.ROLE_BGCOLORS.get(role)

    @staticmethod
    def get_text(role: str):
        return VisualRole.ROLE_TEXT.get(role)

    @staticmethod
    def get_word_hint(role: str):
        return VisualRole.ROLE_WORD_HINT.get(role)
