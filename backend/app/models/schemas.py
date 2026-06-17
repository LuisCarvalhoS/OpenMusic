from pydantic import BaseModel


class AudioInfo(BaseModel):
    """Typed audio metadata extracted from a YouTube video."""

    video_id: str
    title: str
    uploader: str
    artist: str
    album: str
    duration: int
    stream_url: str
    webpage_url: str
    thumbnail_url: str


class DownloadRequest(BaseModel):
    url: str
    download_dir: str | None = None
    folder_name: str | None = None


class OpenFolderRequest(BaseModel):
    path: str


class DownloadResponse(BaseModel):
    id: str
    title: str
    uploader: str
    artist: str
    album: str
    filename: str
    duration: int
    filepath: str
    thumbnail_url: str
