"""Download audio from YouTube as WAV (pcm_s16le, 48kHz, stereo).

Usage:
    python download.py <youtube_url>

Example:
    python download.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
"""

import sys

from app.config import Settings
from app.services.converter import AudioConverter
from app.services.youtube import YouTubeService


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python download.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]
    settings = Settings()
    youtube = YouTubeService()
    converter = AudioConverter(settings)

    print("Fetching audio info...")
    info = youtube.extract_audio_info(url)
    print(f"  Title:    {info.title}")
    print(f"  Channel:  {info.uploader}")
    print(f"  Duration: {info.duration}s")

    safe_title = youtube.sanitize_filename(info.title)
    output_path = f"{settings.downloads_dir}/{safe_title}.wav"

    print("Converting to WAV...")
    converter.convert_to_wav(info.stream_url, output_path)
    print(f"Done: {output_path}")


if __name__ == "__main__":
    main()
