"""
PyDownloader Studio — Redesigned Interface
Lógica separada da UI, design moderno e profissional com CustomTkinter.
"""

import customtkinter as ctk
import webbrowser
import yt_dlp
import threading
from tkinter import messagebox, filedialog
import os

# ══════════════════════════════════════════════
#  LÓGICA DE NEGÓCIO (Backend / Core)
# ══════════════════════════════════════════════

class DownloaderCore:
    """Encapsula toda a lógica de download e busca, sem dependências de UI."""

    def __init__(self):
        self.current_music = None
        self.current_playlist = []
        self.auth_method = "browser"
        self.selected_browser = "chrome"
        self.cookie_file_path = None

    def set_auth_browser(self, browser: str):
        self.auth_method = "browser"
        self.selected_browser = browser

    def set_auth_file(self, path: str):
        self.auth_method = "file"
        self.cookie_file_path = path

    def get_auth_opts(self) -> dict:
        opts = {}
        if self.auth_method == "browser":
            opts["cookiesfrombrowser"] = (self.selected_browser,)
        elif self.auth_method == "file" and self.cookie_file_path:
            opts["cookiefile"] = self.cookie_file_path
        return opts

    def search(self, query: str, on_result, on_playlist, on_status, on_error):
        """Busca música/playlist. Callbacks são chamados na thread worker."""
        ydl_opts = {"quiet": True, "extract_flat": True}
        ydl_opts.update(self.get_auth_opts())

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if "youtube.com" in query or "youtu.be" in query:
                    info = ydl.extract_info(query, download=False)
                    if "entries" in info:
                        self.current_playlist = []
                        for video in info["entries"]:
                            if not video:
                                continue
                            title = video.get("title", "Sem título")
                            link = f"https://www.youtube.com/watch?v={video.get('id')}"
                            self.current_playlist.append(link)
                            on_result(title, link)
                        on_playlist(len(self.current_playlist))
                    else:
                        self.current_playlist = []
                        title = info.get("title", "Desconhecido")
                        on_result(title, query)
                        on_status(f"Vídeo encontrado: {title}")
                else:
                    self.current_playlist = []
                    results = ydl.extract_info(f"ytsearch5:{query}", download=False)
                    for video in results["entries"]:
                        on_result(
                            video["title"],
                            f"https://www.youtube.com/watch?v={video['id']}"
                        )
                    on_status("Busca concluída.")
        except Exception as e:
            on_error(str(e))

    def select_music(self, title: str, link: str):
        self.current_music = {"title": title, "link": link}

    def listen(self):
        if self.current_music:
            webbrowser.open(self.current_music["link"])

    def download_mp3(self, on_status, on_error, save_dir=None):
        if not self.current_music:
            on_error("Nenhuma música selecionada.")
            return
        output = os.path.join(save_dir, "%(title)s.%(ext)s") if save_dir else "%(title)s.%(ext)s"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        }
        ydl_opts.update(self.get_auth_opts())
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.current_music["link"]])
            on_status(f"✅ Download concluído: {self.current_music['title']}")
        except Exception as e:
            on_error(str(e))

    def download_playlist(self, on_status, on_error, save_dir=None):
        if not self.current_playlist:
            on_error("Nenhuma playlist carregada.")
            return
        folder = os.path.join(save_dir, "playlist") if save_dir else "playlist"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        }
        ydl_opts.update(self.get_auth_opts())
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(self.current_playlist)
            on_status(f"✅ Playlist baixada: {len(self.current_playlist)} faixas")
        except Exception as e:
            on_error(str(e))


# ══════════════════════════════════════════════
#  COMPONENTES DE UI REUTILIZÁVEIS
# ══════════════════════════════════════════════

DARK   = "#0d0d0f"
PANEL  = "#141417"
CARD   = "#1c1c21"
BORDER = "#2a2a32"
ACCENT = "#6c63ff"
ACCENT2= "#00d4aa"
MUTED  = "#4a4a5a"
TEXT   = "#e8e8f0"
SUBTEXT= "#8888a0"

FONT_TITLE  = ("Courier New", 22, "bold")
FONT_LABEL  = ("Courier New", 11, "bold")
FONT_BODY   = ("Courier New", 11)
FONT_SMALL  = ("Courier New", 9)
FONT_MONO   = ("Courier New", 10)


def styled_button(parent, text, command, color=ACCENT, width=130, height=36, **kwargs):
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=color, hover_color=_darken(color),
        text_color=TEXT, font=FONT_LABEL,
        corner_radius=6, width=width, height=height,
        **kwargs
    )


def _darken(hex_color):
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    factor = 0.75
    return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"


class SectionLabel(ctk.CTkLabel):
    def __init__(self, parent, text, **kwargs):
        super().__init__(
            parent, text=text.upper(),
            font=FONT_SMALL, text_color=ACCENT,
            **kwargs
        )


class ResultItem(ctk.CTkFrame):
    """Linha clicável para um resultado de busca."""
    def __init__(self, parent, title, link, on_select, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=6, **kwargs)

        self.configure(cursor="hand2")
        self._title = title
        self._link  = link

        self.indicator = ctk.CTkLabel(self, text="▌", font=FONT_BODY, text_color=ACCENT, width=14)
        self.indicator.grid(row=0, column=0, padx=(6, 2), pady=6)

        self.lbl = ctk.CTkLabel(self, text=title, font=FONT_BODY, text_color=TEXT,
                                 anchor="w", wraplength=500)
        self.lbl.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=6)
        self.grid_columnconfigure(1, weight=1)

        for widget in (self, self.indicator, self.lbl):
            widget.bind("<Enter>", lambda e: self.configure(fg_color=BORDER))
            widget.bind("<Leave>", lambda e: self.configure(fg_color="transparent"))
            widget.bind("<Button-1>", lambda e: on_select(title, link))


# ══════════════════════════════════════════════
#  JANELA PRINCIPAL
# ══════════════════════════════════════════════

class PyDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.core = DownloaderCore()
        # Padrão: mesma pasta onde o .py está sendo executado
        self.save_dir = os.path.dirname(os.path.abspath(__file__))

        self.title("PyDownloader Studio")
        self.geometry("1140x720")
        self.minsize(860, 600)
        self.configure(fg_color=DARK)

        self._build_layout()

    # ── Layout Principal ──────────────────────

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self._build_sidebar()
        self._build_main()
        self._build_statusbar()

    # ── Sidebar ───────────────────────────────

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=230, fg_color=PANEL,
                           corner_radius=0, border_width=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(sb, fg_color=CARD, corner_radius=0)
        logo_frame.pack(fill="x")
        ctk.CTkLabel(logo_frame, text="⬛ PyDownloader",
                     font=FONT_TITLE, text_color=ACCENT).pack(pady=22, padx=16)

        # Separador
        ctk.CTkFrame(sb, height=1, fg_color=BORDER).pack(fill="x")

        # Seção Autenticação
        auth_container = ctk.CTkFrame(sb, fg_color="transparent")
        auth_container.pack(fill="x", padx=16, pady=18)

        SectionLabel(auth_container, "◆ Autenticação").pack(anchor="w", pady=(0, 10))

        self.auth_var = ctk.StringVar(value="browser")
        ctk.CTkRadioButton(auth_container, text="Usar navegador", variable=self.auth_var,
                           value="browser", command=self._toggle_auth,
                           font=FONT_BODY, text_color=TEXT,
                           fg_color=ACCENT, border_color=MUTED).pack(anchor="w", pady=3)
        ctk.CTkRadioButton(auth_container, text="Usar cookies.txt", variable=self.auth_var,
                           value="file", command=self._toggle_auth,
                           font=FONT_BODY, text_color=TEXT,
                           fg_color=ACCENT, border_color=MUTED).pack(anchor="w", pady=3)

        self.browser_menu = ctk.CTkOptionMenu(
            auth_container, values=["chrome", "firefox", "edge", "brave", "opera"],
            command=lambda c: self.core.set_auth_browser(c),
            fg_color=CARD, button_color=BORDER, button_hover_color=ACCENT,
            text_color=TEXT, font=FONT_BODY, corner_radius=6
        )
        self.browser_menu.pack(fill="x", pady=(10, 0))
        self.browser_menu.set("chrome")

        self.cookie_btn = styled_button(auth_container, "📂 Carregar cookies.txt",
                                        self._load_cookie, color=CARD, width=195)
        self.cookie_btn.configure(border_width=1, border_color=BORDER)
        # Começa oculto
        self.cookie_lbl = ctk.CTkLabel(auth_container, text="", font=FONT_SMALL,
                                        text_color=ACCENT2, wraplength=180)
        self.cookie_lbl.pack(fill="x")

        # Seção Pasta de destino
        ctk.CTkFrame(sb, height=1, fg_color=BORDER).pack(fill="x", pady=4)
        dest_container = ctk.CTkFrame(sb, fg_color="transparent")
        dest_container.pack(fill="x", padx=16, pady=12)
        SectionLabel(dest_container, "◆ Destino").pack(anchor="w", pady=(0, 8))

        dest_btn = styled_button(dest_container, "📁 Escolher pasta",
                                  self._choose_dir, color=CARD, width=195)
        dest_btn.configure(border_width=1, border_color=BORDER)
        dest_btn.pack(fill="x", pady=(0, 6))

        default_path = os.path.dirname(os.path.abspath(__file__))
        self.dest_lbl = ctk.CTkLabel(dest_container,
                                      text=self._short_path(default_path),
                                      font=FONT_SMALL, text_color=ACCENT2,
                                      wraplength=180, justify="left")
        self.dest_lbl.pack(anchor="w", pady=(0, 4))

        self.dest_reset_btn = ctk.CTkButton(
            dest_container, text="↺ Restaurar padrão",
            command=self._reset_dir,
            fg_color="transparent", hover_color=BORDER,
            text_color=MUTED, font=FONT_SMALL,
            height=22, corner_radius=4, border_width=0
        )
        self.dest_reset_btn.pack(anchor="w")

        # Dica
        ctk.CTkFrame(sb, height=1, fg_color=BORDER).pack(fill="x", pady=4)
        hint = ctk.CTkLabel(sb,
            text="💡 Se o navegador falhar,\nuse a extensão\n'Get cookies.txt'\nna Chrome Web Store.",
            font=FONT_SMALL, text_color=MUTED, justify="center")
        hint.pack(side="bottom", pady=20)

    # ── Main Area ─────────────────────────────

    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=24, pady=20)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)

        # Barra de busca
        search_row = ctk.CTkFrame(main, fg_color="transparent")
        search_row.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        search_row.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="🔍  Pesquisar música ou colar link do YouTube...",
            height=46, font=FONT_BODY, fg_color=CARD,
            border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color=MUTED,
            corner_radius=8
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._search())

        self.search_btn = styled_button(search_row, "Buscar", self._search,
                                         color=ACCENT, width=100, height=46)
        self.search_btn.grid(row=0, column=1)

        # Painel de música selecionada
        self._build_player_card(main)

        # Lista de resultados
        self._build_results_panel(main)

    def _build_player_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=10,
                             border_width=1, border_color=BORDER)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(16, 4))
        SectionLabel(top, "◆ Selecionado agora").pack(side="left")

        self.now_label = ctk.CTkLabel(
            card, text="— Nenhuma faixa selecionada —",
            font=("Courier New", 14, "bold"), text_color=SUBTEXT,
            wraplength=700, anchor="center"
        )
        self.now_label.pack(pady=(4, 14), padx=20)

        # Botões de ação
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=(0, 18))

        styled_button(btn_row, "▶  Ouvir", self._listen,
                       color="#1a6e4a", height=38).pack(side="left", padx=5)
        styled_button(btn_row, "⬇  MP3", self._download_mp3,
                       color=ACCENT, height=38).pack(side="left", padx=5)
        styled_button(btn_row, "📂  Playlist", self._download_playlist,
                       color="#4a4abf", height=38).pack(side="left", padx=5)
        styled_button(btn_row, "✖  Limpar", self._clear,
                       color="#6e1a1a", height=38).pack(side="left", padx=5)

    def _build_results_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=10,
                              border_width=1, border_color=BORDER)
        panel.grid(row=2, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(panel, fg_color=PANEL, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        SectionLabel(header, "◆ Resultados").pack(side="left", padx=16, pady=10)

        self.count_lbl = ctk.CTkLabel(header, text="", font=FONT_SMALL, text_color=SUBTEXT)
        self.count_lbl.pack(side="right", padx=16)

        self.results_scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent",
                                                      scrollbar_button_color=BORDER,
                                                      scrollbar_button_hover_color=ACCENT)
        self.results_scroll.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.results_scroll.grid_columnconfigure(0, weight=1)

        self._result_count = 0
        self._show_empty_state()

    # ── Status Bar ────────────────────────────

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, fg_color=PANEL, height=34, corner_radius=0,
                            border_width=0)
        bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)

        self.status_dot = ctk.CTkLabel(bar, text="●", font=("Courier New", 12),
                                        text_color=ACCENT2, width=20)
        self.status_dot.pack(side="left", padx=(14, 4), pady=6)

        self.status_lbl = ctk.CTkLabel(bar, text="Pronto.", font=FONT_SMALL,
                                        text_color=SUBTEXT, anchor="w")
        self.status_lbl.pack(side="left", fill="x")

    # ── Helpers de UI ─────────────────────────

    def _set_status(self, text, color=ACCENT2):
        self.status_dot.configure(text_color=color)
        self.status_lbl.configure(text=text)

    def _show_empty_state(self):
        lbl = ctk.CTkLabel(self.results_scroll,
                            text="Os resultados aparecerão aqui.\nFaça uma busca ou cole um link.",
                            font=FONT_BODY, text_color=MUTED, justify="center")
        lbl.grid(row=0, column=0, pady=40)

    def _clear_results(self):
        for w in self.results_scroll.winfo_children():
            w.destroy()
        self._result_count = 0
        self.count_lbl.configure(text="")

    def _add_result(self, title, link):
        def on_select(t, l):
            self.core.select_music(t, l)
            self.now_label.configure(text=t, text_color=TEXT, font=("Courier New", 14, "bold"))
            self._set_status(f"Selecionado: {t}")

        item = ResultItem(self.results_scroll, title, link, on_select)
        item.grid(row=self._result_count, column=0, sticky="ew", padx=8, pady=2)
        self._result_count += 1
        self.count_lbl.configure(text=f"{self._result_count} resultado(s)")

    # ── Callbacks de UI ───────────────────────

    def _toggle_auth(self):
        if self.auth_var.get() == "browser":
            self.cookie_btn.pack_forget()
            self.browser_menu.pack(fill="x", pady=(10, 0))
        else:
            self.browser_menu.pack_forget()
            self.cookie_btn.pack(fill="x", pady=(10, 0))

    def _load_cookie(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.core.set_auth_file(path)
            name = os.path.basename(path)
            self.cookie_lbl.configure(text=f"✓ {name}")
            self._set_status(f"Cookie carregado: {name}")

    def _short_path(self, path: str, max_len: int = 28) -> str:
        """Retorna caminho truncado com '...' no meio se muito longo."""
        if len(path) <= max_len:
            return path
        half = (max_len - 3) // 2
        return path[:half] + "..." + path[-half:]

    def _choose_dir(self):
        path = filedialog.askdirectory(initialdir=self.save_dir,
                                        title="Selecionar pasta de destino")
        if path:
            self.save_dir = path
            self.dest_lbl.configure(text=self._short_path(path), text_color=ACCENT2)
            self._set_status(f"Destino: {path}")

    def _reset_dir(self):
        default = os.path.dirname(os.path.abspath(__file__))
        self.save_dir = default
        self.dest_lbl.configure(text=self._short_path(default), text_color=ACCENT2)
        self._set_status("Destino restaurado para o padrão.")

    def _search(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        self._clear_results()
        self._set_status("Buscando...", ACCENT)

        def worker():
            self.core.search(
                query,
                on_result=lambda t, l: self.after(0, self._add_result, t, l),
                on_playlist=lambda n: self.after(0, self._set_status, f"Playlist: {n} faixas", ACCENT2),
                on_status=lambda s: self.after(0, self._set_status, s),
                on_error=lambda e: self.after(0, self._on_error, e)
            )

        threading.Thread(target=worker, daemon=True).start()

    def _listen(self):
        self.core.listen()

    def _download_mp3(self):
        def worker():
            self.after(0, self._set_status, "Baixando MP3...", ACCENT)
            self.core.download_mp3(
                on_status=lambda s: self.after(0, self._set_status, s),
                on_error=lambda e: self.after(0, self._on_error, e),
                save_dir=self.save_dir
            )
        threading.Thread(target=worker, daemon=True).start()

    def _download_playlist(self):
        def worker():
            self.after(0, self._set_status, "Baixando playlist...", ACCENT)
            self.core.download_playlist(
                on_status=lambda s: self.after(0, self._set_status, s),
                on_error=lambda e: self.after(0, self._on_error, e),
                save_dir=self.save_dir
            )
        threading.Thread(target=worker, daemon=True).start()

    def _clear(self):
        self.core.current_music = None
        self.now_label.configure(text="— Nenhuma faixa selecionada —",
                                  text_color=SUBTEXT, font=("Courier New", 14, "bold"))
        self._set_status("Seleção limpa.", SUBTEXT)

    def _on_error(self, msg):
        self._set_status(f"Erro: {msg}", "#e74c3c")
        messagebox.showerror("Erro", msg)


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════

if __name__ == "__main__":
    app = PyDownloaderApp()
    app.mainloop()
