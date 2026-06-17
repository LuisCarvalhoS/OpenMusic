import os
import shutil
import subprocess

import ffmpeg

from app.config import Settings


class AudioConverter:
    """Service for converting audio streams to WAV format using ffmpeg."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._ffmpeg: str | None = None

    def _get_ffmpeg(self) -> str:
        if self._ffmpeg is None:
            self._ffmpeg = self._find_ffmpeg()
        return self._ffmpeg

    @staticmethod
    def _find_ffmpeg() -> str:
        """Locate the ffmpeg binary on the system.

        Returns:
            Path to the ffmpeg executable.

        Raises:
            FileNotFoundError: If ffmpeg is not found.
        """
        found = shutil.which("ffmpeg")
        if found:
            return found

        raise FileNotFoundError(
            "ffmpeg not found. Install it with:\n"
            "  Linux: sudo apt install ffmpeg\n"
            "  macOS: brew install ffmpeg\n"
            "  Windows: winget install ffmpeg"
        )

    def convert_to_wav(
        self,
        stream_url: str,
        output_path: str,
        title: str = "",
        artist: str = "",
        album: str = "",
    ) -> str:
        """Convert an audio stream URL directly to a WAV file with embedded metadata.

        No intermediate files are created — the stream is piped directly
        through ffmpeg and written as WAV.

        Args:
            stream_url: URL of the audio stream.
            output_path: Full path where the WAV file will be saved.
            title: Track title for WAV metadata.
            artist: Artist name for WAV metadata.
            album: Album name for WAV metadata.

        Returns:
            The output_path of the generated WAV file.

        Raises:
            subprocess.CalledProcessError: If ffmpeg fails to process the stream.
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        cmd = [
            self._get_ffmpeg(),
            "-loglevel", "error",
            "-i", stream_url,
            "-f", self._settings.audio_format,
            "-acodec", self._settings.audio_codec,
            "-ar", str(self._settings.audio_sample_rate),
            "-ac", str(self._settings.audio_channels),
        ]

        if title:
            cmd.extend(["-metadata", f"title={title}"])
        if artist:
            cmd.extend(["-metadata", f"artist={artist}"])
        if album:
            cmd.extend(["-metadata", f"album={album}"])

        cmd.extend(["-y", output_path])

        subprocess.run(cmd, check=True, capture_output=True, text=True)

        return output_path

    def check_ffmpeg_available(self) -> bool:
        """Verify that ffmpeg is installed and accessible."""
        try:
            found = shutil.which("ffmpeg")
            if not found:
                return False
            ffmpeg.input("dummy").output("-", format="null", loglevel="quiet").compile(cmd=found)
            return True
        except (ffmpeg.Error, FileNotFoundError):
            return False
