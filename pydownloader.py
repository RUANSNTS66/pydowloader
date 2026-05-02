import yt_dlp
import os
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

# --- GUI Configuration ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PyDownloaderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PYDOWNLOADER STABLE - Modern GUI")
        self.geometry("700x500")

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # 1. Title
        self.label_title = ctk.CTkLabel(self, text="PYDOWNLOADER", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=20)

        # 2. URL Input
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Cole o link do vídeo ou playlist aqui...", width=500)
        self.url_entry.grid(row=1, column=0, padx=20, pady=10)

        # 3. Folder Selection
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.grid(row=2, column=0, padx=20, pady=10)
        
        self.folder_entry = ctk.CTkEntry(self.folder_frame, placeholder_text="Pasta de destino", width=400)
        self.folder_entry.pack(side="left", padx=10, pady=10)
        self.folder_entry.insert(0, os.getcwd()) # Default to current dir

        self.btn_browse = ctk.CTkButton(self.folder_frame, text="Procurar", width=100, command=self.browse_folder)
        self.btn_browse.pack(side="left", padx=10, pady=10)

        # 4. Action Buttons
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.grid(row=3, column=0, padx=20, pady=20)

        self.btn_video = ctk.CTkButton(self.btn_frame, text="Baixar Vídeo", command=lambda: self.start_thread("video"))
        self.btn_video.grid(row=0, column=0, padx=10, pady=10)

        self.btn_mp3 = ctk.CTkButton(self.btn_frame, text="Baixar MP3", command=lambda: self.start_thread("mp3"))
        self.btn_mp3.grid(row=0, column=1, padx=10, pady=10)

        self.btn_convert = ctk.CTkButton(self.btn_frame, text="Converter Pasta MP4->MP3", 
                                         fg_color="#D35400", hover_color="#A04000", 
                                         command=self.start_conversion_thread)
        self.btn_convert.grid(row=0, column=2, padx=10, pady=10)

        # 5. Log/Status Area
        self.log_area = ctk.CTkTextbox(self, width=600, height=150)
        self.log_area.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")
        self.log_message("Sitema pronto. Aguardando comando...")

    # --- Helper Functions ---
    def log_message(self, text):
        """Adds text to the GUI log area."""
        self.log_area.insert("end", f"{text}\n")
        self.log_area.see("end")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def start_thread(self, mode):
        """Runs the download logic in a separate thread to prevent GUI freezing."""
        url = self.url_entry.get().strip()
        pasta = self.folder_entry.get().strip()

        if not url:
            messagebox.showwarning("Erro", "Por favor, insira a URL do vídeo.")
            return

        threading.Thread(target=self.download_logic, args=(url, pasta, mode), daemon=True).start()

    def start_conversion_thread(self):
        """Runs the conversion logic in a separate thread."""
        pasta = self.folder_entry.get().strip()
        if not pasta or not os.path.exists(pasta):
            messagebox.showwarning("Erro", "Selecione uma pasta válida primeiro.")
            return
        
        threading.Thread(target=self.conversion_logic, args=(pasta,), daemon=True).start()

    # ==============================
    # CORE LOGIC (Integrated from original script)
    # ==============================

    def download_logic(self, url, pasta, mode):
        try:
            self.log_message(f"Iniciando download ({mode})...")
            
            if not os.path.exists(pasta):
                os.makedirs(pasta)

            if mode == "mp3":
                formato = "bestaudio/best"
                posprocess = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                formato = "bestvideo+bestaudio/best"
                posprocess = []

            opcoes = {
                "outtmpl": os.path.join(pasta, "%(title)s.%(ext)s"),
                "format": formato,
                "postprocessors": posprocess,
                "cookiefile": "cookies.txt",
                "http_headers": {"User-Agent": "Mozilla/5.0"},
                "sleep_interval": 3,
                "max_sleep_interval": 6,
            }

            with yt_dlp.YoutubeDL(opcoes) as ydl:
                ydl.download([url])

            self.log_message("✅ Download concluído com sucesso!")
            messagebox.showinfo("Sucesso", "Download finalizado!")

        except Exception as e:
            self.log_message(f"❌ Erro: {e}")
            messagebox.showerror("Erro", f"Erro durante o download: {e}")

    def conversion_logic(self, pasta):
        try:
            self.log_message(f"Analisando pasta: {pasta}")
            arquivos = [f for f in os.listdir(pasta) if f.lower().endswith(".mp4")]

            if not arquivos:
                self.log_message("Nenhum arquivo MP4 encontrado.")
                return

            self.log_message(f"Convertendo {len(arquivos)} arquivos...")

            for arquivo in arquivos:
                caminho_mp4 = os.path.join(pasta, arquivo)
                nome_mp3 = os.path.splitext(arquivo)[0] + ".mp3"
                caminho_mp3 = os.path.join(pasta, nome_mp3)

                subprocess.run([
                    "ffmpeg", "-i", caminho_mp4, "-vn", "-ab", "192k", caminho_mp3
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                os.remove(caminho_mp4)
                self.log_message(f"Convertido: {arquivo}")

            self.log_message("✅ Conversão finalizada.")
            messagebox.showinfo("Sucesso", "Todos os arquivos foram convertidos!")

        except Exception as e:
            self.log_message(f"❌ Erro na conversão: {e}")
            messagebox.showerror("Erro", f"Erro na conversão: {e}")

if __name__ == "__main__":
    app = PyDownloaderGUI()
    app.mainloop()
