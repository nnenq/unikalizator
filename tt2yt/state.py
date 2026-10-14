"""Учёт видео: что уже скачано, подготовлено, описано и загружено.

Всё хранится в одном JSON-файле data/state.json, его можно открыть и поправить руками.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# Порядок, в котором видео проходит этапы.
NEW = "new"
DOWNLOADED = "downloaded"
PREPARED = "prepared"
DESCRIBED = "described"
UPLOADED = "uploaded"
SKIPPED = "skipped"
FAILED = "failed"

STATUS_RU = {
    NEW: "найдено",
    DOWNLOADED: "скачано",
    PREPARED: "подготовлено",
    DESCRIBED: "описано",
    UPLOADED: "на YouTube",
    SKIPPED: "пропущено",
    FAILED: "ошибка",
}


class State:
    def __init__(self, path: Path):
        self.path = path
        self.videos: dict[str, dict] = {}
        if path.exists():
            self.videos = json.loads(path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(self.videos, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        os.replace(tmp, self.path)

    def __contains__(self, video_id: str) -> bool:
        return video_id in self.videos

    def get(self, video_id: str) -> dict | None:
        return self.videos.get(video_id)

    def update(self, video_id: str, **fields) -> dict:
        video = self.videos.setdefault(video_id, {"id": video_id, "status": NEW})
        video.update(fields)
        self.save()
        return video

    def with_status(self, *statuses: str, newest_first: bool = False) -> list[dict]:
        found = [v for v in self.videos.values() if v["status"] in statuses]
        found.sort(key=lambda v: (v.get("upload_date") or "", v["id"]), reverse=newest_first)
        return found
