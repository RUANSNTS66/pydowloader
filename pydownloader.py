import yt_dlp
import os
import subprocess

while True:
    print("\n=== PYDOWNLOADER ===")

    print("\nO que você quer fazer?")
    print("1 - Baixar vídeo")
    print("2 - Baixar como MP3")
    print("3 - Converter MP4 de uma pasta para MP3")

    modo = input("Escolha: ").strip()

    # ==============================
    # CONVERTER MP4 -> MP3
    # ==============================
    if modo == "3":
        pasta = input("Digite o caminho da pasta com os MP4: ").strip()

        if not os.path.exists(pasta):
            print("Pasta não encontrada.")
        else:
            arquivos = [f for f in os.listdir(pasta) if f.lower().endswith(".mp4")]

            if not arquivos:
                print("Nenhum arquivo MP4 encontrado.")
            else:
                print(f"\nConvertendo {len(arquivos)} arquivos...\n")

                for arquivo in arquivos:
                    caminho_mp4 = os.path.join(pasta, arquivo)
                    nome_mp3 = os.path.splitext(arquivo)[0] + ".mp3"
                    caminho_mp3 = os.path.join(pasta, nome_mp3)

                    try:
                        subprocess.run([
                            "ffmpeg",
                            "-i", caminho_mp4,
                            "-vn",
                            "-ab", "192k",
                            caminho_mp3
                        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        os.remove(caminho_mp4)

                        print(f"Convertido: {arquivo}")

                    except Exception as e:
                        print(f"Erro em {arquivo}: {e}")

                print("\nConversão finalizada.")

    # ==============================
    # DOWNLOAD
    # ==============================
    elif modo in ["1", "2"]:
        url = input("\nCole o link do video ou playlist: ").strip()

        pasta = input("Pasta para salvar (ENTER = atual): ").strip()

        if pasta == "":
            pasta = os.getcwd()

        if not os.path.exists(pasta):
            os.makedirs(pasta)

        if modo == "2":
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

            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            },

            "sleep_interval": 3,
            "max_sleep_interval": 6,
        }

        try:
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                ydl.download([url])

            print("\nDownload concluído com sucesso.")

        except Exception as e:
            print("\nErro durante o download:", e)

    else:
        print("Opção inválida.")

    # ==============================
    # LOOP FINAL
    # ==============================
    print("\nO que você quer fazer agora?")
    print("1 - Fazer outra operação")
    print("2 - Sair")

    escolha = input("Escolha: ").strip()

    if escolha == "2":
        print("Encerrando...")
        break