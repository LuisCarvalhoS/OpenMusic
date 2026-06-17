import os
import subprocess
import sys
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings
from app.models.schemas import DownloadRequest, DownloadResponse, OpenFolderRequest
from app.services.converter import AudioConverter
from app.services.youtube import YouTubeService

router = APIRouter(prefix="/api/audio", tags=["audio"])


def get_settings() -> Settings:
    return Settings()


def get_youtube_service() -> YouTubeService:
    return YouTubeService()


def get_audio_converter(settings: Annotated[Settings, Depends(get_settings)]) -> AudioConverter:
    return AudioConverter(settings)


SettingsDep = Annotated[Settings, Depends(get_settings)]
YouTubeServiceDep = Annotated[YouTubeService, Depends(get_youtube_service)]
AudioConverterDep = Annotated[AudioConverter, Depends(get_audio_converter)]


def _build_filename(service: YouTubeService, title: str) -> str:
    return f"{service.sanitize_filename(title)}.wav"


def _resolve_dir(request_dir: str | None, settings: Settings) -> str:
    """Use the request-provided directory or fall back to settings default."""
    target = request_dir or settings.downloads_dir
    os.makedirs(target, exist_ok=True)
    return target


def _process_download(
    url: str,
    download_dir: str,
    settings: Settings,
    youtube: YouTubeService,
    converter: AudioConverter,
) -> DownloadResponse:
    """Shared logic for downloading a single video."""
    try:
        info = youtube.extract_audio_info(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch video info: {e}") from e

    filename = _build_filename(youtube, info.title)
    output_path = os.path.join(download_dir, filename)

    try:
        converter.convert_to_wav(
            info.stream_url, output_path,
            title=info.title, artist=info.artist, album=info.album,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio conversion failed: {e}") from e

    return DownloadResponse(
        id=info.video_id,
        title=info.title,
        uploader=info.uploader,
        artist=info.artist,
        album=info.album,
        filename=filename,
        duration=info.duration,
        filepath=output_path,
        thumbnail_url=info.thumbnail_url,
    )


@router.post("/download")
def download_audio(
    request: DownloadRequest,
    settings: SettingsDep,
    youtube: YouTubeServiceDep,
    converter: AudioConverterDep,
) -> DownloadResponse:
    """Download the best quality audio from a YouTube video and convert to WAV."""
    download_dir = _resolve_dir(request.download_dir, settings)
    return _process_download(request.url, download_dir, settings, youtube, converter)


@router.post("/download-playlist")
def download_playlist(
    request: DownloadRequest,
    settings: SettingsDep,
    youtube: YouTubeServiceDep,
    converter: AudioConverterDep,
) -> list[DownloadResponse]:
    """Download all videos from a YouTube playlist as WAV files."""
    download_dir = _resolve_dir(request.download_dir, settings)

    if request.folder_name:
        safe_folder = youtube.sanitize_filename(request.folder_name)
        download_dir = os.path.join(download_dir, safe_folder)
        os.makedirs(download_dir, exist_ok=True)

    try:
        infos = youtube.extract_playlist_info(request.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch playlist: {e}") from e

    results: list[DownloadResponse] = []
    for info in infos:
        try:
            filename = _build_filename(youtube, info.title)
            output_path = os.path.join(download_dir, filename)
            converter.convert_to_wav(
                info.stream_url, output_path,
                title=info.title, artist=info.artist, album=info.album,
            )
            results.append(
                DownloadResponse(
                    id=info.video_id,
                    title=info.title,
                    uploader=info.uploader,
                    artist=info.artist,
                    album=info.album,
                    filename=filename,
                    duration=info.duration,
                    filepath=output_path,
                    thumbnail_url=info.thumbnail_url,
                )
            )
        except Exception:
            continue

    return results


@router.post("/open-folder")
def open_folder(request: OpenFolderRequest) -> dict:
    """Open a folder in the system file explorer.

    Intended for local use only.
    """
    path = request.path
    directory = os.path.dirname(path) if os.path.isfile(path) else path

    if not os.path.exists(directory):
        raise HTTPException(status_code=400, detail=f"Path does not exist: {directory}")

    try:
        if sys.platform == "win32":
            os.startfile(directory)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", directory])  # noqa: S603, S607
        else:
            subprocess.Popen(["xdg-open", directory])  # noqa: S603, S607
        return {"opened": directory}
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/health")
def health_check(converter: AudioConverterDep) -> dict:
    """Check if ffmpeg is available."""
    return {
        "ffmpeg_available": converter.check_ffmpeg_available(),
    }
