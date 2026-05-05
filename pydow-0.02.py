import customtkinter as ctk
import webbrowser
import yt_dlp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MusicApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Enigma Music App")
        self.geometry("900x650")

        self.title_label = ctk.CTkLabel(self, text="🎧 Enigma Music", font=("Arial", 28, "bold"))
        self.title_label.pack(pady=10)

        self.search_entry = ctk.CTkEntry(self, placeholder_text="Pesquisar música ou colar link...")
        self.search_entry.pack(pady=10, padx=20, fill="x")

        self.search_button = ctk.CTkButton(self, text="Buscar", command=self.search_music)
        self.search_button.pack(pady=5)

        self.results_frame = ctk.CTkScrollableFrame(self, width=700, height=300)
        self.results_frame.pack(pady=10)

        self.card_frame = ctk.CTkFrame(self, width=400, height=150)
        self.card_frame.pack(pady=20)

        self.card_label = ctk.CTkLabel(self.card_frame, text="Nenhuma música selecionada", wraplength=350)
        self.card_label.pack(pady=20)

        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.pack()

        ctk.CTkButton(self.buttons_frame, text="▶ Ouvir", fg_color="green", command=self.like_music).grid(row=0, column=0, padx=10)
        ctk.CTkButton(self.buttons_frame, text="⬇ MP3", fg_color="purple", command=self.download_mp3).grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.buttons_frame, text="✖ Pular", fg_color="red", command=self.skip_music).grid(row=0, column=2, padx=10)
        ctk.CTkButton(self.buttons_frame, text="⬇ Playlist", fg_color="orange", command=self.download_playlist).grid(row=0, column=3, padx=10)

        self.current_music = None
        self.current_playlist = None

    def search_music(self):
        query = self.search_entry.get()

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not query:
            return

        ydl_opts = {'quiet': True, 'extract_flat': True}

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if "youtube.com" in query or "youtu.be" in query:
                    info = ydl.extract_info(query, download=False)

                    if 'entries' in info:
                        self.current_playlist = []

                        for video in info['entries']:
                            if not video:
                                continue

                            title = video.get('title', 'Sem título')
                            link = f"https://www.youtube.com/watch?v={video.get('id')}"
                            self.current_playlist.append(link)

                            btn = ctk.CTkButton(self.results_frame, text=title, anchor="w",
                                command=lambda t=title, l=link: self.select_music(t, l))
                            btn.pack(fill="x", pady=5)

                        self.card_label.configure(text=f"Playlist carregada ({len(self.current_playlist)} músicas)")
                    else:
                        self.current_playlist = None
                        self.select_music(info.get('title', 'Sem título'), query)
                else:
                    self.current_playlist = None
                    results = ydl.extract_info(f"ytsearch5:{query}", download=False)

                    for video in results['entries']:
                        title = video['title']
                        link = f"https://www.youtube.com/watch?v={video['id']}"

                        btn = ctk.CTkButton(self.results_frame, text=title, anchor="w",
                            command=lambda t=title, l=link: self.select_music(t, l))
                        btn.pack(fill="x", pady=5)

        except Exception as e:
            ctk.CTkLabel(self.results_frame, text=f"Erro: {e}").pack()

    def select_music(self, title, link):
        self.current_music = {"title": title, "link": link}
        self.card_label.configure(text=title)

    def like_music(self):
        if self.current_music:
            webbrowser.open(self.current_music["link"])

    def download_mp3(self):
        if not self.current_music:
            self.card_label.configure(text="Nenhuma música selecionada")
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.current_music["link"]])

            self.card_label.configure(text="Download concluído 🎧")
        except Exception as e:
            self.card_label.configure(text=f"Erro: {e}")

    def download_playlist(self):
        if not self.current_playlist:
            self.card_label.configure(text="Nenhuma playlist carregada")
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'playlist/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(self.current_playlist)

            self.card_label.configure(text="Playlist baixada 🎧🔥")
        except Exception as e:
            self.card_label.configure(text=f"Erro: {e}")

    def skip_music(self):
        self.card_label.configure(text="Pulado... escolha outra música")
        self.current_music = None


if __name__ == "__main__":
    app = MusicApp()
    app.mainloop()
