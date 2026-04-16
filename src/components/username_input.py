import flet as ft

from src.components.mandatory_field import MandatoryField

class UsernameInput(ft.AlertDialog):
    def __init__(self):
        
        self.done_button: ft.Button = ft.Button('Listo', disabled=True, align=ft.Alignment.CENTER)
        self.username_field: MandatoryField = MandatoryField('Nombre de jugador', True, self.on_change_field)
        self.username_text: str | None = None
        
        super().__init__(
            title=ft.Text('Bienvenido a Impostor TCP', color='#f52f83'),
            content=ft.Column([
                
                ft.Text(
                    '¿Cuál es tu nombre?',
                    size=18
                ),
                self.username_field
            ], tight=True),

            actions=[self.done_button],
            modal=True,
            open=True
        )

    def on_change_field(self):
        if self.username_field.is_unlocked:
            self.done_button.disabled = False
        else:
            self.username_text = None
            self.done_button.disabled = True

        self.update()
