import customtkinter as ctk
from src.components.visual_player import VisualPlayer


class GameApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Impostor TCP")
        self.geometry("800x600")
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear VisualPlayer (maneja todo el flujo)
        self.visual_player = VisualPlayer(self)


if __name__ == "__main__":
    app = GameApp()
    app.mainloop()