import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NEO_")

    downloads_dir: str = os.path.join(os.path.expanduser("~"), "Music", "OpenMusic")
    audio_sample_rate: int = 48000
    audio_codec: str = "pcm_s24le"
    audio_channels: int = 2
    audio_format: str = "wav"
