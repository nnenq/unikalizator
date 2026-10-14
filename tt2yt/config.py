"""Загрузка настроек из config.toml."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path


class ConfigError(Exception):
    pass


@dataclass
class TikTokConfig:
    accounts: list[str] = field(default_factory=list)
    username: str = ""  # одиночный аккаунт — то же, что accounts = ["..."]
    max_videos: int = 30
    min_views: int = 0
    top_share: float = 1.0
    cookies_file: str = ""
    cookies_from_browser: str = ""


def normalize_account(value: str) -> str:
    """'https://www.tiktok.com/@ella.stewart8?_r=1' или '@ella.stewart8' -> 'ella.stewart8'."""
    value = value.strip()
    m = re.search(r"@([\w.\-]+)", value)
    if m:
        return m.group(1)
    return value.split("?")[0].strip("/ ")


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

    t = cfg.tiktok
    accounts = list(t.accounts) + ([t.username] if t.username else [])
    t.accounts = list(dict.fromkeys(a for a in map(normalize_account, accounts) if a))
    t.username = ""
    if not 0 < t.top_share <= 1:
        raise ConfigError("[tiktok] top_share должно быть от 0 до 1 (1 — все видео)")
    if cfg.youtube.privacy not in ("private", "unlisted", "public"):
        raise ConfigError("[youtube] privacy должно быть private, unlisted или public")
    if cfg.youtube.order not in ("oldest", "newest"):
        raise ConfigError("[youtube] order должно быть oldest или newest")
    return cfg
