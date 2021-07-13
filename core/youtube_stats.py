import codecs
import json
import urllib.request

from core import utils
from pytube import YouTube

previousprogress = 0


def on_progress(stream, chunk, bytes_remaining):
    global previousprogress
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining

    liveprogress = int(bytes_downloaded / total_size * 100)
    if liveprogress > previousprogress:
        previousprogress = liveprogress
        print(liveprogress)


class YouTubeStats:  # Classe per gestionar les dades JSON i altres funcions del video
    def __init__(self, url: str):  # Agafar i llegir les dades JSON de la llista amb la API
        try:
            self.json_url = urllib.request.urlopen(url)
        except Exception as e:
            print(f"Exception: {e}")
        self.data = json.loads(self.json_url.read())

    def get_video_id(self, n: int):  # Pillar la ID del video "n" de la pagina actual
        return self.data["items"][n]["snippet"]["resourceId"]["videoId"]

    def get_video_title(self, n: int):  # Pillar el títol del video "n" de la pagina actual
        return self.data["items"][n]["snippet"]["title"]

    def get_next_token(self):  # Pillar el token de la seguent pàgina
        return self.data["nextPageToken"]

    def get_total_videos(self):  # Total de videos a la llista
        return self.data["pageInfo"]["totalResults"]

    def get_page_videos(self):  # Nº de videos a la pàgina actual
        return len(self.data["items"])

    def download_video(self, youtube_url: str, title: str):  # Descarregar el video amb el títol
        youtube = YouTube(youtube_url)
        # youtube.register_on_progress_callback(on_progress)
        youtube.streams.get_highest_resolution().download(output_path="output", filename=f"{title}")
