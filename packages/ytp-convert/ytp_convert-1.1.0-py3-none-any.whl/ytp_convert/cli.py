import argparse
from .downloader import PlaylistDownloader
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Convert a YouTube playlist into a single combined file."
    )
    parser.add_argument("url", help="YouTube playlist URL to download")
    parser.add_argument(
        "-o", "--output",
        default="combined",
        help="Output filename (default: combined.<format>)"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Continue downloading the rest of the playlist even if some videos fail."
    )
    parser.add_argument(
        "--format",
        default="mp3",
        choices=["mp3", "mp4"],
        help="File Format to save the playlist download as. (default: mp3)"
    )
    args = parser.parse_args()

    downloader = PlaylistDownloader(args.url)
    try:
        downloader.downloadPlaylist(format=args.format, output_name=args.output, ignore_errors=args.force)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()