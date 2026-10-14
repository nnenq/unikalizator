"""Загрузка на YouTube через YouTube Data API v3."""

from __future__ import annotations

import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import Config
from .meta import Meta

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeError(Exception):
    pass


class QuotaExceeded(YouTubeError):
    pass


def get_service(cfg: Config):
    try:
        from google.auth.exceptions import RefreshError
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as e:
        raise YouTubeError(
            "не установлены библиотеки Google: pip install -r requirements.txt"
        ) from e

    secrets = cfg.path(cfg.youtube.client_secrets)
    token = cfg.path(cfg.youtube.token_file)

    creds = None
    if token.exists():
        creds = Credentials.from_authorized_user_file(str(token), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            creds = None  # доступ отозван — авторизуемся заново
    if not creds or not creds.valid:
        if not secrets.exists():
            raise YouTubeError(
                f"не найден {secrets.name}. Как его получить — см. README, раздел «Подключение YouTube»"
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(secrets), SCOPES)
        print("Откроется браузер: войдите в Google-аккаунт канала и разрешите загрузку видео.")
        creds = flow.run_local_server(port=0)
        token.write_text(creds.to_json(), encoding="utf-8")

    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def upload(service, path: Path, meta: Meta, cfg: Config, publish_at: str | None = None) -> str:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    y = cfg.youtube
    status = {
        "privacyStatus": "private" if publish_at else y.privacy,
        "selfDeclaredMadeForKids": y.made_for_kids,
    }
    if publish_at:
        status["publishAt"] = publish_at
    body = {
        "snippet": {
            "title": meta.title,
            "description": meta.description,
            "tags": meta.tags,
            "categoryId": y.category_id,
            "defaultLanguage": "ru",
            "defaultAudioLanguage": "ru",
        },
        "status": status,
    }
    media = MediaFileUpload(str(path), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    response, retries = None, 0
    while response is None:
        try:
            _, response = request.next_chunk()
        except HttpError as e:
            reason = _reason(e)
            if reason in ("quotaExceeded", "uploadLimitExceeded"):
                raise QuotaExceeded(
                    "исчерпан дневной лимит загрузок YouTube API, продолжим завтра"
                ) from e
            if e.resp.status in (500, 502, 503, 504) and retries < 5:
                retries += 1
                time.sleep(2**retries)
                continue
            raise YouTubeError(f"YouTube вернул ошибку {e.resp.status}: {reason or e}") from e
    return response["id"]


def _reason(error) -> str:
    try:
        return error.error_details[0].get("reason", "")
    except (AttributeError, IndexError, TypeError):
        return ""


def next_slots(
    taken: set[str],
    times: list[str],
    tz_name: str,
    count: int,
    now: datetime | None = None,
) -> list[str]:
    """Ближайшие свободные слоты публикации в формате RFC 3339 (UTC).

    taken — уже занятые слоты в том же формате, times — время публикации на каждый день
    («12:00»), tz_name — часовой пояс, в котором указано время.
    """
    tz = ZoneInfo(tz_name)
    now = now or datetime.now(timezone.utc)
    earliest = now + timedelta(hours=1)  # YouTube требует время в будущем
    clock = sorted(datetime.strptime(t, "%H:%M").time() for t in times)
    if not clock:
        raise ValueError("[youtube] times пуст")

    slots: list[str] = []
    day: date = now.astimezone(tz).date()
    while len(slots) < count:
        for t in clock:
            moment = datetime.combine(day, t, tzinfo=tz).astimezone(timezone.utc)
            stamp = moment.strftime("%Y-%m-%dT%H:%M:%SZ")
            if moment >= earliest and stamp not in taken and stamp not in slots:
                slots.append(stamp)
                if len(slots) == count:
                    break
        day += timedelta(days=1)
    return slots
