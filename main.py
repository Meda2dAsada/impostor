import flet as ft
from src.components.visual_client import VisualClient
from src.components.role_display import RoleDisplay


def main(page: ft.Page):
    #page.window.center()

    page.add(VisualClient(0, '', 0))

    page.update()




if __name__ == '__main__':
    ft.run(main)


