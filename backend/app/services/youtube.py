import re

import yt_dlp

from app.models.schemas import AudioInfo


class YouTubeService:
    """Service for extracting audio metadata and stream URLs from YouTube."""

    _AUDIO_DL_OPTS = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
    }

    def extract_audio_info(self, url: str) -> AudioInfo:
        """Extract metadata and the best audio stream URL for a given YouTube video.

        Args:
            url: YouTube video URL.

        Returns:
            AudioInfo with video_id, title, uploader, duration, stream_url, webpage_url.

        Raises:
            ValueError: If the URL cannot be processed or no audio stream found.
        """
        with yt_dlp.YoutubeDL(self._AUDIO_DL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        stream_url = self._pick_best_audio_url(info)
        return AudioInfo(
            video_id=info.get("id", ""),
            title=info.get("title", "unknown"),
            uploader=info.get("uploader", "unknown"),
            artist=info.get("artist") or info.get("uploader", "unknown"),
            album=info.get("album") or "",
            duration=info.get("duration", 0) or 0,
            stream_url=stream_url,
            webpage_url=info.get("webpage_url", url),
            thumbnail_url=info.get("thumbnail", ""),
        )

    def extract_playlist_info(self, playlist_url: str) -> list[AudioInfo]:
        """Extract audio info for all videos in a YouTube playlist.

        Args:
            playlist_url: YouTube playlist URL.

        Returns:
            List of AudioInfo for each video in the playlist.

        Raises:
            ValueError: If the URL cannot be processed or the playlist is empty.
        """
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "extract_flat": True}) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)

        entries = playlist_info.get("entries", [])
        if not entries:
            raise ValueError(f"No videos found in playlist: {playlist_url}")

        results: list[AudioInfo] = []
        for entry in entries:
            if not entry:
                continue
            video_url = entry.get("url") or entry.get("webpage_url")
            if not video_url:
                continue
            try:
                results.append(self.extract_audio_info(video_url))
            except Exception:
                continue

        return results

    @staticmethod
    def sanitize_filename(title: str) -> str:
        """Remove invalid characters from a filename."""
        return re.sub(r'[<>:"/\\|?*]', "_", title)

    @staticmethod
    def _pick_best_audio_url(info: dict) -> str:
        """Select the audio stream with the highest bitrate from yt-dlp info."""
        formats = info.get("formats", [])
        audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]
        if not audio_formats:
            audio_formats = [f for f in formats if f.get("acodec") != "none"]

        if not audio_formats:
            raise ValueError("No audio stream found")

        best_audio = max(audio_formats, key=lambda f: f.get("abr", 0) or 0)
        return best_audio["url"]
