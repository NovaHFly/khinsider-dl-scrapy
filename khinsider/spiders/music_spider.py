from pathlib import Path
from urllib.parse import unquote

from scrapy import Spider
from scrapy.http import Response

DOWNLOADS = Path("Downloads")
DOWNLOADS.mkdir(exist_ok=True)


class MusicSpider(Spider):
    name = "khinsider_music"

    start_urls = [*Path("albums.txt").read_text(encoding="UTF-8").splitlines()]

    def parse(self, response: Response):
        album_name = response.css("h2::text").get()
        yield from response.follow_all(
            css="#songlist tr td.playlistDownloadSong a",
            callback=self.get_song_url,
            cb_kwargs={"album_name": album_name},
        )

    def get_song_url(self, response: Response, **kwargs):
        src = response.css("audio::attr(src)").get()
        yield response.follow(src, callback=self.download_file, cb_kwargs=kwargs)

    def download_file(self, response: Response, album_name: str):
        filename: str = unquote(response.url.split("/")[-1])
        dl_path = DOWNLOADS / album_name / filename
        dl_path.parent.mkdir(exist_ok=True, parents=True)
        dl_path.write_bytes(response.body)
