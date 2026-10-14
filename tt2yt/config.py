"""Загрузка настроек из config.toml."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path


class ConfigError(Exception):
    pass


@dataclass
class TikTokConfig:
    username: str = ""
    max_videos: int = 30
    cookies_file: str = ""
    cookies_from_browser: str = ""


@dataclass
class VideoConfig:
    width: int = 1080
    height: int = 1920
    crf: int = 20
    normalize_audio: bool = True


@dataclass
class MetaConfig:
    use_ai: bool = True
    model: str = "claude-opus-5-5"
    effort: str = "medium"
    frames: int = 4
    channel_topic: str = "теории, загадки, тайны и необъяснимые истории"
    default_tags: list[str] = field(
        default_factory=lambda: ["теории", "загадки", "тайны", "необъяснимое"]
    )
    footer: str = "Подписывайся, чтобы не пропустить новые теории!"


@dataclass
class YouTubeConfig:
    client_secrets: str = "client_secret.json"
    token_file: str = "token.json"
    privacy: str = "private"
    category_id: str = "24"
    made_for_kids: bool = False
    schedule: bool = False
    times: list[str] = field(default_factory=lambda: ["12:00", "18:00"])
    timezone: str = "Europe/Moscow"
    max_uploads_per_run: int = 5
    order: str = "oldest"


@dataclass
class Config:
    base_dir: Path
    data_dir: Path
    tiktok: TikTokConfig
    video: VideoConfig
    meta: MetaConfig
    youtube: YouTubeConfig

    def path(self, value: str) -> Path:
        """Относительные пути в конфиге считаются от папки, где лежит config.toml."""
        p = Path(value).expanduser()
        return p if p.is_absolute() else self.base_dir / p


def _section(cls, raw: dict, name: str):
    known = {f.name for f in fields(cls)}
    unknown = set(raw) - known
    if unknown:
        raise ConfigError(
            f"[{name}]: неизвестные параметры {', '.join(sorted(unknown))}. "
            f"Допустимые: {', '.join(sorted(known))}"
        )
    return cls(**raw)


def load_config(path: Path) -> Config:
    if not path.exists():
        raise ConfigError(
            f"Не найден файл настроек {path}. Создайте его командой: python -m tt2yt init"
        )
    with path.open("rb") as f:
        try:
            raw = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ConfigError(f"Ошибка в {path}: {e}") from e

    base_dir = path.resolve().parent
    cfg = Config(
        base_dir=base_dir,
        data_dir=base_dir / raw.pop("data_dir", "data"),
        tiktok=_section(TikTokConfig, raw.pop("tiktok", {}), "tiktok"),
        video=_section(VideoConfig, raw.pop("video", {}), "video"),
        meta=_section(MetaConfig, raw.pop("meta", {}), "meta"),
        youtube=_section(YouTubeConfig, raw.pop("youtube", {}), "youtube"),
    )
    if raw:
        raise ConfigError(f"Неизвестные разделы в {path}: {', '.join(sorted(raw))}")

    cfg.tiktok.username = cfg.tiktok.username.strip().lstrip("@")
    if cfg.youtube.privacy not in ("private", "unlisted", "public"):
        raise ConfigError("[youtube] privacy должно быть private, unlisted или public")
    if cfg.youtube.order not in ("oldest", "newest"):
        raise ConfigError("[youtube] order должно быть oldest или newest")
    return cfg
