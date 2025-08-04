import os
import shutil

from yt_dlp import YoutubeDL


class Downloader():
    def __init__(self, dir=None, cleanup=False):
        if dir is None:
            if cleanup:
                os.rmdir("./temp")
            if not os.path.isdir("./temp"):
                os.mkdir("./temp")
            self.dir = "./temp"
        else:
            self.dir = dir
        self.ydl_opts_download = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.dir, 'cache/%(title)s.%(ext)s'),
            'replace_metadata_attributes': [('title', x, '_') for x in r'\/|:*?<>"'],
            'ignoreerrors': True,
            'quiet': True,
        }
        self.ydl_opts_playlist = {
            'extract_flat': True,
            'quiet': True
        }

    def process_url(self, url):
        if url.startswith("https://www.youtube.com/playlist?list="):
            urls = []
            with YoutubeDL(self.ydl_opts_playlist) as ydl:
                playlist_info = ydl.extract_info(url, download=False)
                urls += [e['url'] for e in playlist_info['entries'] if e is not None]
        elif url.startswith("https://www.youtube.com/watch?v=") or url.startswith("https://youtu.be/"):
            urls = [url]
        else:
            raise Exception("Invalid URL")
        return urls

    def download_video(self, url):
        if os.path.isdir(os.path.join(self.dir, 'cache')):
            shutil.rmtree(os.path.join(self.dir, 'cache'))
        os.mkdir(os.path.join(self.dir, 'cache'))
        for u in self.process_url(url):
            try:
                with YoutubeDL(self.ydl_opts_download) as ydl:
                    info = ydl.extract_info(u, download=False)
                    filename = '.'.join(os.path.basename(ydl.prepare_filename(info)).split('.')[:-1])
                    if not os.path.exists(os.path.join(self.dir, filename + ".mp3")):
                        print(f"Downloading {filename}")
                        ydl.download([u])
                        os.rename(os.path.join(self.dir, 'cache', filename + ".mp3"), os.path.join(self.dir, filename + ".mp3"))
                    else:
                        print(f"{filename} already exists")
            except Exception as e:
                print(f"Failed to download {u}: {e}")
        os.rmdir(os.path.join(self.dir, 'cache'))


if __name__ == "__main__":
    import subprocess
    command = ['python', './music_manager.py', '--path', './temp']
    if os.name == 'nt':
        subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)
    elif os.name == 'posix':
        subprocess.Popen(['gnome-terminal', '--'] + command)
    else:
        raise Exception(f"OS not supported: {os.name}")
    dl = Downloader()
    while True:
        url = input("> ")
        if url.lower() == "q":
            print("Program terminated.")
            break
        try:
            dl.download_video(url)
        except Exception as e:
            print(e)