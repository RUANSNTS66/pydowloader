import customtkinter as ctk
import webbrowser
import yt_dlp
import threading
from tkinter import messagebox, filedialog

# --- Configuration & Theme ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_ACCENT = "#1f6aa5" 
COLOR_BG_DARK = "#1a1a1a" 
COLOR_BG_LIGHT = "#2b2b2b" 

class MusicApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyDownloader Studio")
        self.geometry("1100x700")

        # State variables
        self.current_music = None
        self.current_playlist = None
        self.selected_browser = "chrome" 
        self.cookie_file_path = None # Path to manual cookies.txt

        # --- Main Layout ---
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=4) 
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_content()
        self.setup_status_bar()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=COLOR_BG_DARK, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="PyDownloader", 
                                      font=("Segoe UI", 24, "bold"))
        self.logo_label.pack(pady=30, padx=20)

        # --- Authentication Section ---
        self.auth_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.auth_frame.pack(pady=10, padx=20, fill="x")

        self.browser_label = ctk.CTkLabel(self.auth_frame, text="Auth Method:", font=("Segoe UI", 13, "bold"))
        self.browser_label.pack(pady=(10, 5))

        # Option to choose between Browser or File
        self.method_var = ctk.StringVar(value="browser")
        self.radio_browser = ctk.CTkRadioButton(self.auth_frame, text="Use Browser", 
                                                variable=self.method_var, value="browser", 
                                                command=self.toggle_auth_ui)
        self.radio_browser.pack(pady=5, anchor="w")

        self.radio_file = ctk.CTkRadioButton(self.auth_frame, text="Use cookies.txt", 
                                             variable=self.method_var, value="file", 
                                             command=self.toggle_auth_ui)
        self.radio_file.pack(pady=5, anchor="w")

        # Browser Selector (Only shown if 'browser' is selected)
        self.browser_menu = ctk.CTkOptionMenu(self.auth_frame, 
                                              values=["chrome", "firefox", "edge", "brave", "opera"],
                                              command=self.change_browser)
        self.browser_menu.pack(pady=10, padx=10)
        self.browser_menu.set("chrome")

        # Cookie File Button (Only shown if 'file' is selected)
        self.file_btn = ctk.CTkButton(self.auth_frame, text="Load cookies.txt", 
                                      fg_color=COLOR_BG_LIGHT, border_width=1,
                                      command=self.load_cookie_file)
        # Hidden by default until 'file' is selected

        self.info_label = ctk.CTkLabel(self.sidebar, 
                                      text="Tip: If browser fails,\nuse 'Get cookies.txt' extension\nfrom Chrome Web Store.", 
                                      font=("Segoe UI", 10), text_color="gray", justify="center")
        self.info_label.pack(side="bottom", pady=20)

    def toggle_auth_ui(self):
        """Shows/Hides UI elements based on authentication method"""
        if self.method_var.get() == "browser":
            self.browser_menu.pack(pady=10, padx=10)
            self.file_btn.pack_forget()
        else:
            self.browser_menu.pack_forget()
            self.file_btn.pack(pady=10, padx=10)

    def change_browser(self, choice):
        self.selected_browser = choice

    def load_cookie_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.cookie_file_path = path
            self.update_status(f"Cookie file loaded: {path.split('/')[-1]}")

    def setup_main_content(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        self.search_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        self.search_entry = ctk.CTkEntry(self.search_frame, 
                                         placeholder_text="Search for music or paste YouTube link...",
                                         height=45, font=("Segoe UI", 14))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.search_button = ctk.CTkButton(self.search_frame, text="Search", 
                                           width=100, height=45, 
                                           font=("Segoe UI", 14, "bold"),
                                           command=self.search_music)
        self.search_button.pack(side="right")

        self.results_frame = ctk.CTkScrollableFrame(self.main_container, 
                                                    label_text="Search Results",
                                                    fg_color=COLOR_BG_LIGHT)
        self.results_frame.grid(row=1, column=0, sticky="nsew", pady=10)

        self.card_frame = ctk.CTkFrame(self.main_container, 
                                       fg_color=COLOR_BG_LIGHT, 
                                       border_width=2, border_color=COLOR_ACCENT)
        self.card_frame.grid(row=2, column=0, sticky="ew", pady=20)

        self.card_label = ctk.CTkLabel(self.card_frame, text="No song selected", 
                                      font=("Segoe UI", 16, "italic"), wraplength=600)
        self.card_label.pack(pady=(20, 10))

        self.btn_group = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.btn_group.pack(pady=(0, 20))

        self.btn_listen = ctk.CTkButton(self.btn_group, text="▶ Listen", fg_color="#2ecc71", 
                                        hover_color="#27ae60", width=100, command=self.listen_music)
        self.btn_listen.grid(row=0, column=0, padx=5)

        self.btn_mp3 = ctk.CTkButton(self.btn_group, text="⬇ Download MP3", 
                                     command=lambda: self.start_thread(self.download_mp3))
        self.btn_mp3.grid(row=0, column=1, padx=5)

        self.btn_playlist = ctk.CTkButton(self.btn_group, text="📂 Playlist", 
                                           command=lambda: self.start_thread(self.download_playlist))
        self.btn_playlist.grid(row=0, column=2, padx=5)

        self.btn_clear = ctk.CTkButton(self.btn_group, text="✖ Clear", fg_color="#e74c3c", 
                                      hover_color="#c0392b", width=100, command=self.skip_music)
        self.btn_clear.grid(row=0, column=3, padx=5)

    def setup_status_bar(self):
        self.status_bar = ctk.CTkLabel(self, text="Ready", font=("Segoe UI", 11), 
                                      text_color="gray", anchor="w")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=5)

    # --- Logic ---

    def update_status(self, text):
        self.status_bar.configure(text=f"Status: {text}")

    def start_thread(self, target_function):
        thread = threading.Thread(target=target_function, daemon=True)
        thread.start()

    def get_auth_opts(self):
        """Returns the cookie configuration based on the selected method"""
        opts = {}
        if self.method_var.get() == "browser":
            opts['cookiesfrombrowser'] = (self.selected_browser,)
        elif self.method_var.get() == "file" and self.cookie_file_path:
            opts['cookiefile'] = self.cookie_file_path
        return opts

    def search_music(self):
        query = self.search_entry.get()
        if not query: return

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        self.update_status("Searching...")
        
        def perform_search():
            ydl_opts = {'quiet': True, 'extract_flat': True}
            ydl_opts.update(self.get_auth_opts())
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    if "youtube.com" in query or "youtu.be" in query:
                        info = ydl.extract_info(query, download=False)
                        if 'entries' in info:
                            self.current_playlist = []
                            for video in info['entries']:
                                if not video: continue
                                title = video.get('title', 'Unknown Title')
                                link = f"https://www.youtube.com/watch?v={video.get('id')}"
                                self.current_playlist.append(link)
                                self.add_result_button(title, link)
                            self.card_label.configure(text=f"Playlist loaded: {len(self.current_playlist)} songs")
                        else:
                            self.current_playlist = None
                            self.select_music(info.get('title', 'Unknown'), query)
                    else:
                        self.current_playlist = None
                        results = ydl.extract_info(f"ytsearch5:{query}", download=False)
                        for video in results['entries']:
                            self.add_result_button(video['title'], f"https://www.youtube.com/watch?v={video['id']}")
                self.update_status("Search complete.")
            except Exception as e:
                self.update_status(f"Error: {str(e)}")

        threading.Thread(target=perform_search, daemon=True).start()

    def add_result_button(self, title, link):
        btn = ctk.CTkButton(self.results_frame, text=f" 🎵 {title}", 
                            anchor="w", fg_color="transparent", 
                            text_color="white", hover_color=COLOR_BG_DARK,
                            command=lambda t=title, l=link: self.select_music(t, l))
        btn.pack(fill="x", pady=2)

    def select_music(self, title, link):
        self.current_music = {"title": title, "link": link}
        self.card_label.configure(text=f"Selected: {title}", font=("Segoe UI", 16, "bold"))
        self.update_status(f"Selected {title}")

    def listen_music(self):
        if self.current_music:
            webbrowser.open(self.current_music["link"])

    def download_mp3(self):
        if not self.current_music:
            messagebox.showwarning("Warning", "Please select a song first!")
            return

        self.update_status(f"Downloading {self.current_music['title']}...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        }
        ydl_opts.update(self.get_auth_opts())

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.current_music["link"]])
            self.update_status("Download successful! 🎧")
        except Exception as e:
            self.update_status(f"Download failed: {e}")

    def download_playlist(self):
        if not self.current_playlist:
            messagebox.showwarning("Warning", "No playlist loaded!")
            return

        self.update_status("Downloading entire playlist...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'playlist/%(title)s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        }
        ydl_opts.update(self.get_auth_opts())

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(self.current_playlist)
            self.update_status("Playlist downloaded successfully! 🔥")
        except Exception as e:
            self.update_status(f"Playlist error: {e}")

    def skip_music(self):
        self.current_music = None
        self.card_label.configure(text="No song selected", font=("Segoe UI", 16, "italic"))
        self.update_status("Selection cleared.")

if __name__ == "__main__":
    app = MusicApp()
    app.mainloop()
