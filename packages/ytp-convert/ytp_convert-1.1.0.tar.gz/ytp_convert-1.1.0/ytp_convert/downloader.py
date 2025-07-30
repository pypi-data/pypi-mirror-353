from pydub import AudioSegment
import tempfile
import os
from yt_dlp import YoutubeDL
from yt_dlp.utils import (
    DownloadError,
    ExtractorError,
    UnsupportedError,
)
from urllib.parse import urlparse, parse_qs
from typing import List
import subprocess

class PlaylistDownloader:
    """
    Downloads a YouTube playlist and combines all tracks into a single media file. Supports audio only or audio and video downloads. 
    Audio files downloaded as mp3, and video files downloaded as mp4. 
    
    Attributes:
        playlist_link (str): The URL of the YouTube playlist to process.
    """
    class QuietLogger:
        def debug(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): print(f"❌ {msg}")


    def __init__(self, playlist_url: str):
        """
        Initialize the PlaylistDownloader with a YouTube playlist URL.
        
        Args:
            playlist_url (str): The URL of the YouTube playlist.
        """
        if not self._is_valid_playlist_url(playlist_url):
            raise ValueError(f"Invalid YouTube playlist URL - {playlist_url}")
        
        self.playlist_link = playlist_url
        self.total_videos: int = 0
        self.completed_downloads: int = 0
        self.tmpdir = ""
    
    def _progress_hook(self, d):
        if d['status'] == 'finished':
            filename = os.path.basename(d['filename'])
            if filename.endswith(("mp3", "mp4")):
                self.completed_downloads += 1
                print(f"✅ ({self.completed_downloads}/{self.total_videos}) Finished: {filename}")

    def _is_valid_playlist_url(self, url: str) -> bool:
        """
        Validates whether the URL is a valid YouTube playlist URL.

        Args:
            url (str): The URL to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        parsed = urlparse(url)

        if not parsed.scheme.startswith("http"):
            return False
        if "youtube.com" not in parsed.netloc:
            return False
        if not parsed.path.startswith("/playlist"):
            return False
        query_params = parse_qs(parsed.query)
        list_param = query_params.get("list", [""])[0]

        return bool(list_param.strip())

    def _write_ffmpeg_txt_file(self, files: List[str], concat_path: str) -> None:
        """
        Helper to write .txt of media files for ffmpeg to concatenate together.

        Args:
            files (List[str]): list of media files to concatenate
            concat_path (str): path to open the .txt file
        """
        with open(concat_path, "w") as f:
            for file in files:
                f.write(f"file '{os.path.abspath(os.path.join(self.tmpdir, file))}'\n")


    def _combine_files(self, files: List[str], format: str, output_file: str) -> None:
        """
        Helper to concatenate a list of media files together. Concatenation order is done in the order the files appear 
        in the list of files. 

        Args:
            files (List[str]): list of files to combine (as file paths)
            format (str): format of the media file (mp3 or mp4)
            output_file (str): name of the final combined file 
        """
        if format == "mp3":
            combined = AudioSegment.empty()
            for fname in files:
                path = os.path.join(self.tmpdir, fname)
                combined += AudioSegment.from_file(path)

            combined.export(output_file, format="mp3")
        elif format == "mp4":
            concat_path = os.path.join(self.tmpdir, "concat.txt")
            intermediate_file = os.path.join(self.tmpdir, "temp_combined.mp4")
            self._write_ffmpeg_txt_file(files, concat_path)
            # concat mp4s
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_path,
                "-c", "copy",
                "-loglevel", "error",
                "-hide_banner",
                intermediate_file
            ]
            subprocess.run(cmd, check=True)
            # re-encode audio to AAC
            codec_cmd = [
                "ffmpeg",
                "-i", intermediate_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-loglevel", "error",
                "-hide_banner",
                output_file
            ]
            subprocess.run(codec_cmd, check=True)
        else:
            raise ValueError("Unexpected File Format in combine_files()")

    def _get_ydl_opts(self, format: str, ignore_errors: bool) -> dict:
        """
        Getter for ydl optional args based on the specified format. 
        Args:
            format (str): media format (mp3 or mp4)
            ignore_errors (bool): optional ydl flag, obtained as an arg from the user. 
        Returns:
            dict: ydl options as a dictionary
        """
        if format == "mp3":
            return {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.tmpdir, '%(playlist_index)03d_%(title).200s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._progress_hook],
                'logger': self.QuietLogger(),
                'noplaylist': False,
                'ignoreerrors': ignore_errors,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        elif format == "mp4":
            return {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join(self.tmpdir, '%(playlist_index)03d_%(title).200s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._progress_hook],
                'logger': self.QuietLogger(),
                'noplaylist': False,
                'ignoreerrors': ignore_errors,
                'merge_output_format': 'mp4'
            }
        else:
            raise ValueError("Unexpected format in get_ydl_opts()")

    def downloadPlaylist(self, format: str, output_name: str, ignore_errors: bool = False) -> None:
        """
        Downloads all audio tracks from the playlist, merges them into a single media file and writes it to disk. 

        Args:
            output_name (str): The filename for the final combined output. Defaults to 'combined.<format>'.
            ignore_errors (bool): Continue downloading the rest of the playlist even if some videos fail.

        Raises:
            Exception: If no media files are downloaded.
        """
        output_name = output_name.strip()
        output_file = f"{output_name}.{format}"
        if not output_file.lower().endswith(f".{format}"):
            raise ValueError(f"Invalid output file - '{output_file}'. The filename must end with '.{format}'")

        with tempfile.TemporaryDirectory(prefix="ytp2mp3_") as tmpdir:
            self.tmpdir = tmpdir
            ydl_opts: dict = self._get_ydl_opts(format=format, ignore_errors=ignore_errors)

            # get num videos in the playlist
            with YoutubeDL({'quiet': True}) as probe:
                info = probe.extract_info(self.playlist_link, download=False)
                self.total_videos = len(info.get('entries', []))
            print(f"🎵 Found {self.total_videos} videos in the playlist.")
            if ignore_errors:
                print("⚠️ 'Force' mode enabled: will skip failed downloads.")
            else:
                print("🚫 'Force' mode not enabled: will abort on first error.")
                  
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    print("\nDownloading playlist...")
                    ydl.download([self.playlist_link])
            except (DownloadError, UnsupportedError, ExtractorError) as e:
                raise RuntimeError(f"Youtube Download Failed: {e}")

            files = sorted(
                [f for f in os.listdir(tmpdir) if f.endswith('.mp3') or f.endswith(".mp4")]
            )

            if not files:
                raise Exception(f"No {format} files found! Playlist may be empty or videos may be inaccessible.")

            print(f"Combining files as {format}...")
            self._combine_files(files, format, output_file)

            print(f"🎧 Combined {format} saved to: {output_file}")
            print("\n📊 Download Summary:")
            print(f"✅ Success: {self.completed_downloads}")
            print(f"❌ Skipped: {self.total_videos - self.completed_downloads}")

# test usage
if __name__ == "__main__":
    url = "https://youtube.com/playlist?list=PLERI1_ESTKAyaWKpE5I_uVpzbzmm4HkI5&si=DxlpgQkG3dBdNXdL" 
    downloader = PlaylistDownloader(url)
    downloader.downloadPlaylist()


    

