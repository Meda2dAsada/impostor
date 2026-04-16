import flet as ft
import asyncio
from src.constants.const import ROLE_COLORS, ROLE_BGCOLORS, ROLE_TEXT

class RoleDisplay(ft.AlertDialog):
    def __init__(self, role: str, word: str | None = None):
        
        color_style = ROLE_COLORS.get(role)

        self.accept_button = ft.TextButton('Aceptar', style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: color_style,
                    ft.ControlState.DISABLED: "gray",
                }, overlay_color=ROLE_BGCOLORS.get(role)
            ), 

            on_click=self.accept_alert, disabled=True
        )

        super().__init__(
            title=ft.Text(ROLE_TEXT.get(role), color=color_style),
            content=ft.Text(
                f'La palabra secreta es: {word}' if word is not None 
                else 'Descubre la palabra secreta.',
                size=20
            ),
            actions=[self.accept_button],
            modal=True, 
            open=True,

        )

    async def unlock_accept_alert(self):
        await asyncio.sleep(5)
        self.accept_button.disabled = False

        self.page.update()

    def accept_alert(self, e: ft.Event):
        self.open = False
        e.page.update()

    def did_mount(self):
        self.running = True
        self.page.run_task(self.unlock_accept_alert)

    def will_unmount(self):
        self.running = False
