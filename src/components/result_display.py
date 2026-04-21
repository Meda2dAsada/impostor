import customtkinter as ctk

class ResultDisplay(ctk.CTkToplevel):
    """
    Diálogo que muestra el resultado del juego.
    """
    
    def __init__(self, master, result_message: str, on_continue=None):
        super().__init__(master)
        
        self.title("🎮 Resultado del Juego")
        self.configure(fg_color="#2E1258")
        self.geometry("500x300")
        self.resizable(False, False)
        
        self.transient(master)
        self.grab_set()
        
        self.on_continue = on_continue
        
        self._setup_ui(result_message)
        
        # Auto-cierre después de 5 segundos
        self.after(5000, self._auto_close)
    
    def _setup_ui(self, result_message: str):
        """Configura la interfaz de resultados."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Icono según resultado
        if "Ganan los Civiles" in result_message or "Civiles" in result_message:
            icon = "🎉"
            color = "#00FF00"
        else:
            icon = "😈"
            color = "#FF4444"
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"{icon} RESULTADO {icon}",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color
        )
        title_label.pack(pady=(0, 20))
        
        # Mensaje de resultado
        result_label = ctk.CTkLabel(
            main_frame,
            text=result_message,
            font=ctk.CTkFont(size=16),
            text_color="#FFFFFF",
            wraplength=400,
            justify="center"
        )
        result_label.pack(pady=20)
        
        # Botón de continuar
        continue_btn = ctk.CTkButton(
            main_frame,
            text="Jugar de nuevo",
            command=self._on_continue,
            fg_color="#7357FF",
            hover_color="#5a3cc4",
            height=40,
            width=200
        )
        continue_btn.pack(pady=20)
    
    def _on_continue(self):
        """Continúa al siguiente juego."""
        self.destroy()
        if self.on_continue:
            self.on_continue()
    
    def _auto_close(self):
        """Auto-cierra el diálogo."""
        if self.winfo_exists():
            self._on_continue()