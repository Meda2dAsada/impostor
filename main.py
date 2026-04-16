import flet as ft
from src.components.visual_client import VisualClient
from src.components.role_display import RoleDisplay


async def main(page: ft.Page):
    await page.window.center()
    page.title = 'Impostor TCP'

    page.add(VisualClient(0))

    page.update()




if __name__ == '__main__':
    ft.run(main)


