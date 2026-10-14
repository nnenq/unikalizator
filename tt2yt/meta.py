"""Название, описание и теги для YouTube.

Если доступен Claude (ANTHROPIC_API_KEY), метаданные пишет ИИ по подписи из TikTok,
автосубтитрам и нескольким кадрам. Иначе — простые правила на основе подписи.
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import MetaConfig

TITLE_MAX = 100
DESCRIPTION_MAX_BYTES = 5000
TAGS_MAX_CHARS = 450  # у YouTube лимит 500, оставляем запас

HASHTAG_RE = re.compile(r"#([\w]+)", re.UNICODE)
# Хэштеги, которые на YouTube бесполезны.
JUNK_HASHTAGS = {
    "fyp", "foryou", "foryoupage", "fy", "рек", "рекомендации", "реки", "врек",
    "хочуврек", "tiktok", "тикток", "viral", "xyzbca", "trend", "тренд",
}


@dataclass
class Meta:
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    source: str = "rules"


def split_caption(caption: str) -> tuple[str, list[str]]:
    """'Текст #тег1 #тег2' -> ('Текст', ['тег1', 'тег2'])."""
    tags = HASHTAG_RE.findall(caption or "")
    text = HASHTAG_RE.sub("", caption or "")
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text, tags


def useful_hashtags(tags: list[str]) -> list[str]:
    seen, result = set(), []
    for t in tags:
        key = t.lower()
        if key in JUNK_HASHTAGS or key in seen:
            continue
        seen.add(key)
        result.append(t)
    return result


def read_subtitles(path: Path | None) -> str:
    """Текст из .vtt/.srt без таймкодов и повторов."""
    if not path or not path.exists():
        return ""
    lines = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if (
            not line
            or line == "WEBVTT"
            or line.isdigit()
            or "-->" in line
            or line.startswith(("NOTE", "Kind:", "Language:"))
        ):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        if not lines or lines[-1] != line:
            lines.append(line)
    return " ".join(lines)


def _clean(text: str) -> str:
    # YouTube отклоняет < и > в названии и описании.
    return text.replace("<", "‹").replace(">", "›").strip()


def _truncate_words(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,.;:-—")
    return cut + "…"


def _fit_tags(tags: list[str]) -> list[str]:
    result, total, seen = [], 0, set()
    for tag in tags:
        tag = _clean(tag.lstrip("#")).replace(",", " ").strip()
        if not tag or tag.lower() in seen:
            continue
        # Теги с пробелами YouTube считает вместе с кавычками, плюс запятая-разделитель.
        cost = len(tag) + (2 if " " in tag else 0) + 1
        if total + cost > TAGS_MAX_CHARS:
            break
        seen.add(tag.lower())
        result.append(tag)
        total += cost
    return result


def sanitize(meta: Meta) -> Meta:
    """Приводит метаданные к ограничениям YouTube."""
    title = _clean(meta.title).strip("«»\"' ")
    title = re.sub(r"\s+", " ", HASHTAG_RE.sub("", title)).strip() or "Новая теория"
    title = _truncate_words(title, TITLE_MAX)

    description = _clean(meta.description)
    while len(description.encode("utf-8")) > DESCRIPTION_MAX_BYTES:
        description = description[: len(description) - 50]

    return Meta(title=title, description=description, tags=_fit_tags(meta.tags), source=meta.source)


def finalize(meta: Meta, cfg: MetaConfig, is_short: bool) -> Meta:
    """Добавляет подпись канала, #shorts и стандартные теги, затем sanitize()."""
    description = meta.description.strip()
    if cfg.footer and cfg.footer not in description:
        description = f"{description}\n\n{cfg.footer}".strip()
    if is_short and "#shorts" not in description.lower():
        description = f"{description}\n#shorts"
    tags = list(meta.tags) + list(cfg.default_tags)
    return sanitize(Meta(title=meta.title, description=description, tags=tags, source=meta.source))


def rule_based(caption: str, cfg: MetaConfig) -> Meta:
    text, hashtags = split_caption(caption)
    hashtags = useful_hashtags(hashtags)

    first_line = text.splitlines()[0] if text else ""
    sentence = re.split(r"(?<=[.!?…])\s", first_line)[0] if first_line else ""
    title = sentence or (hashtags[0].replace("_", " ").capitalize() if hashtags else "")

    description = text
    if hashtags:
        description += "\n\n" + " ".join(f"#{t}" for t in hashtags[:5])
    return Meta(title=title, description=description, tags=hashtags, source="rules")


SYSTEM_PROMPT = """\
Ты — редактор русскоязычного YouTube-канала. Тематика канала: {topic}.
Автор переносит свои короткие вертикальные видео из TikTok на YouTube, а ты пишешь \
для каждого видео название, описание и теги на русском языке.

Название:
- до 70 символов, вызывает любопытство и желание досмотреть, но обещает только то, что \
действительно есть в видео;
- без хэштегов, без символов < и >, без кавычек вокруг всего названия; эмодзи — не больше \
одного и только если уместно.

Описание:
- 2–4 коротких предложения, которые раскрывают интригу ролика и подталкивают досмотреть;
- затем пустая строка и 3–5 хэштегов по теме ролика (#shorts и подпись канала добавятся \
автоматически, их не пиши);
- не упоминай TikTok.

Теги: 8–15 поисковых запросов на русском, по которым зритель стал бы искать такое видео, \
от общих к конкретным, без символа #.

Теории, слухи и необъяснимые истории подавай как версии и гипотезы («есть теория, что…», \
«почему многие верят, что…»), а не как доказанные факты: так ролики не попадают под \
ограничения YouTube за дезинформацию.
Не выдумывай конкретных фактов (имён, дат, цифр), которых нет в подписи, расшифровке или кадрах. \
Если материала мало — опирайся на кадры и общую тему.\
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title", "description", "tags"],
    "additionalProperties": False,
}


class AIUnavailable(Exception):
    """ИИ сейчас недоступен — используем правила."""


class AIWriter:
    def __init__(self, cfg: MetaConfig):
        try:
            import anthropic
        except ImportError as e:
            raise AIUnavailable("не установлен пакет anthropic (pip install anthropic)") from e
        self.anthropic = anthropic
        self.client = anthropic.Anthropic()
        # Ключ из ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN или профиль `ant auth login`.
        if not (
            self.client.api_key
            or self.client.auth_token
            or getattr(self.client, "_token_cache", None) is not None
        ):
            raise AIUnavailable("не задан ключ — переменная окружения ANTHROPIC_API_KEY")
        self.cfg = cfg

    def write(
        self,
        caption: str,
        transcript: str,
        duration: float,
        frames: list[Path],
        recent_titles: list[str],
    ) -> Meta:
        content: list[dict] = []
        for frame in frames:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64.standard_b64encode(frame.read_bytes()).decode("ascii"),
                },
            })
        parts = [
            f"Подпись к видео в TikTok: {caption or '(нет)'}",
            f"Длительность: {round(duration)} сек.",
            f"Расшифровка речи (автосубтитры, могут быть ошибки): {transcript or '(нет)'}",
        ]
        if frames:
            parts.append(f"Выше {len(frames)} кадра(ов) из видео по порядку.")
        if recent_titles:
            parts.append(
                "Недавние названия на канале — не повторяй их формулировки:\n"
                + "\n".join(f"- {t}" for t in recent_titles)
            )
        parts.append("Напиши название, описание и теги для этого видео.")
        content.append({"type": "text", "text": "\n\n".join(parts)})

        anthropic = self.anthropic
        try:
            response = self.client.beta.messages.create(
                model=self.cfg.model,
                max_tokens=16000,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                output_config={
                    "effort": self.cfg.effort,
                    "format": {"type": "json_schema", "schema": SCHEMA},
                },
                system=SYSTEM_PROMPT.format(topic=self.cfg.channel_topic),
                messages=[{"role": "user", "content": content}],
            )
        except anthropic.AuthenticationError as e:
            raise AIUnavailable(
                "нет доступа к Claude API — задайте переменную окружения ANTHROPIC_API_KEY"
            ) from e
        except anthropic.PermissionDeniedError as e:
            raise AIUnavailable(f"у ключа API нет доступа: {e.message}") from e
        except anthropic.APIStatusError as e:
            raise RuntimeError(f"Claude API вернул ошибку {e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise RuntimeError("нет связи с Claude API") from e

        if response.stop_reason == "refusal":
            raise RuntimeError("Claude отказался описывать это видео")
        if response.stop_reason == "max_tokens":
            raise RuntimeError("ответ Claude оборвался")
        text = next(b.text for b in response.content if b.type == "text")
        data = json.loads(text)
        return Meta(
            title=data["title"], description=data["description"], tags=data["tags"], source="ai"
        )


TEXT_TITLE, TEXT_DESCRIPTION, TEXT_TAGS = "НАЗВАНИЕ:", "ОПИСАНИЕ:", "ТЕГИ:"


def to_text(meta: Meta) -> str:
    """youtube.txt: чтобы скопировать в YouTube Studio или поправить перед загрузкой."""
    return (
        f"{TEXT_TITLE}\n{meta.title}\n\n"
        f"{TEXT_DESCRIPTION}\n{meta.description}\n\n"
        f"{TEXT_TAGS}\n{', '.join(meta.tags)}\n"
    )


def from_text(text: str, source: str = "file") -> Meta:
    """Обратно из youtube.txt (возможно, отредактированного вручную)."""
    sections: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        if line.strip() in (TEXT_TITLE, TEXT_DESCRIPTION, TEXT_TAGS):
            current = line.strip()
            sections[current] = []
        elif current:
            sections[current].append(line)
    if TEXT_TITLE not in sections:
        raise ValueError(f"в файле нет раздела {TEXT_TITLE}")

    def joined(key: str) -> str:
        return "\n".join(sections.get(key, [])).strip()

    tags = [t.strip() for t in joined(TEXT_TAGS).replace("\n", ",").split(",")]
    return sanitize(Meta(
        title=" ".join(joined(TEXT_TITLE).split()),
        description=joined(TEXT_DESCRIPTION),
        tags=[t for t in tags if t],
        source=source,
    ))
