import flet as ft
from src.constants.const import LOCKED_MODE_COLOR, UNLOCKED_MODE_COLOR, WAITING_MODE_COLOR


class MandatoryField(ft.TextField):
    def __init__(self, label: str, autofocus: bool, callback: ft.ControlEventHandler[ft.TextField] = None):
        super().__init__(label=label, autofocus=autofocus, border_color=WAITING_MODE_COLOR, on_change=self.on_self_change)
        self.callback = callback

    def on_self_change(self):
        if self.is_unlocked:

            self.border_color = UNLOCKED_MODE_COLOR
        else:

            self.border_color = LOCKED_MODE_COLOR

        self.update()

        if self.callback:
            self.callback()

    
    @property
    def is_unlocked(self) -> bool:
        return bool(self.value.strip())