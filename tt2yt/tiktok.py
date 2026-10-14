"""Скачивание видео из TikTok через yt-dlp."""

from __future__ import annotations

from pathlib import Path

import yt_dlp

from .config import Config


HINT = (
    "Обычно помогает указать cookies_from_browser в config.toml (и быть залогиненным "
    "в TikTok в этом браузере), обновить yt-dlp либо скачивать по ссылкам: "
    "fetch --url <ссылка> или fetch --links links.txt"
)


class TikTokError(Exception):
    pass


class _Logger:
    """Ошибки yt-dlp показываем сами (в TikTokError), чтобы не печатать их дважды."""

    def debug(self, msg: str) -> None:
        pass

    def info(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        print(f"    (yt-dlp) {msg}")

    def error(self, msg: str) -> None:
        pass


def _error_text(e: Exception) -> str:
    return str(e).removeprefix("ERROR: ").split("; please report this issue")[0]


def _base_opts(cfg: Config) -> dict:
    opts: dict = {"quiet": True, "noprogress": True, "logger": _Logger()}
    if cfg.tiktok.cookies_file:
        opts["cookiefile"] = str(cfg.path(cfg.tiktok.cookies_file))
    if cfg.tiktok.cookies_from_browser:
        opts["cookiesfrombrowser"] = (cfg.tiktok.cookies_from_browser,)
    return opts


def list_profile(cfg: Config) -> list[dict]:
    """Последние видео профиля: [{"id", "url"}], от новых к старым."""
    username = cfg.tiktok.username
    if not username:
        raise TikTokError("В config.toml не указан [tiktok] username")

    opts = {
        **_base_opts(cfg),
        "extract_flat": "in_playlist",
        "playlistend": cfg.tiktok.max_videos,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"https://www.tiktok.com/@{username}", download=False)
    except yt_dlp.utils.DownloadError as e:
        raise TikTokError(f"{_error_text(e)}\n{HINT}") from e

    entries = [e for e in (info or {}).get("entries") or [] if e]
    if not entries:
        raise TikTokError(f"TikTok не отдал список видео @{username}.\n{HINT}")
    return [
        {
            "id": str(e["id"]),
            "url": e.get("url") or f"https://www.tiktok.com/@{username}/video/{e['id']}",
        }
        for e in entries
    ]


def download(url: str, dest: Path, cfg: Config) -> dict:
    """Скачивает одно видео (без водяного знака) и русские автосубтитры, если есть."""
    dest.mkdir(parents=True, exist_ok=True)
    opts = {
        **_base_opts(cfg),
        "outtmpl": str(dest / "source.%(ext)s"),
        "merge_output_format": "mp4",
        "overwrites": True,
        "writesubtitles": True,
        "subtitleslangs": ["ru.*", "rus.*"],
        "subtitlesformat": "vtt/srt/best",
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError as e:
        raise TikTokError(_error_text(e)) from e

    downloads = info.get("requested_downloads") or []
    if not downloads:
        raise TikTokError("yt-dlp ничего не скачал (возможно, это фото-пост, а не видео)")

    subtitles = [
        Path(s["filepath"]).name
        for s in (info.get("requested_subtitles") or {}).values()
        if s.get("filepath")
    ]
    return {
        "id": str(info["id"]),
        "url": info.get("webpage_url") or url,
        "caption": info.get("description") or info.get("title") or "",
        "upload_date": info.get("upload_date") or "",
        "source": Path(downloads[0]["filepath"]).name,
        "subtitles": subtitles[0] if subtitles else None,
    }
