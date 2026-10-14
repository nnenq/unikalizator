"""Командная строка: python -m tt2yt <команда>."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from . import meta as meta_mod
from . import state as st
from .config import Config, ConfigError, load_config
from .state import State
from .video import VideoError

EXAMPLE_CONFIG = Path(__file__).resolve().parent.parent / "config.example.toml"


def video_dir(cfg: Config, video_id: str) -> Path:
    return cfg.data_dir / "videos" / video_id


def fail(state: State, video: dict, error: Exception | str, retry_status: str) -> None:
    print(f"  ✗ {video['id']}: {error}")
    state.update(video["id"], status=st.FAILED, error=str(error), retry_status=retry_status)


def short(text: str, limit: int = 60) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


# --- команды ---------------------------------------------------------------


def cmd_init(args) -> int:
    target = Path(args.config)
    if target.exists():
        print(f"{target} уже существует, ничего не меняю.")
        return 0
    text = EXAMPLE_CONFIG.read_text(encoding="utf-8")
    username = args.username
    if username is None and sys.stdin.isatty():
        username = input("Ваш ник в TikTok (без @): ").strip()
    if username:
        text = text.replace('username = ""', f'username = "{username.lstrip("@")}"', 1)
    target.write_text(text, encoding="utf-8")
    print(f"Создан {target}. Откройте его и проверьте настройки.")
    return 0


def cmd_fetch(cfg: Config, state: State, args) -> int:
    from .tiktok import TikTokError, download, list_profile

    urls: list[str] = list(args.url or [])
    if args.links:
        for line in args.links.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)

    if urls:
        for url in urls:
            m = re.search(r"/(?:video|photo)/(\d+)", url)
            # короткие ссылки (vm.tiktok.com/...) получат настоящий ID после скачивания
            key = m.group(1) if m else "url-" + hashlib.sha1(url.encode()).hexdigest()[:10]
            if key not in state:
                state.update(key, url=url, source_kind="tiktok")
    else:
        print(f"Проверяю профиль TikTok @{cfg.tiktok.username}…")
        try:
            entries = list_profile(cfg)
        except TikTokError as e:
            print(f"Не удалось получить список видео: {e}")
            return 1
        new = [e for e in entries if e["id"] not in state]
        for e in new:
            state.update(e["id"], url=e["url"], source_kind="tiktok")
        print(f"В профиле {len(entries)} последних видео, новых: {len(new)}")

    pending = state.with_status(st.NEW)[: args.limit]
    for video in pending:
        print(f"  ↓ {video['url']}")
        try:
            info = download(video["url"], video_dir(cfg, video["id"]), cfg)
        except TikTokError as e:
            fail(state, video, e, st.NEW)
            continue
        if info["id"] != video["id"]:  # ссылка была не на /video/<id>
            del state.videos[video["id"]]
            old_dir = video_dir(cfg, video["id"])
            new_dir = video_dir(cfg, info["id"])
            if info["id"] in state:
                shutil.rmtree(old_dir, ignore_errors=True)
                print(f"    уже есть в списке как {info['id']}")
                state.save()
                continue
            if new_dir.exists():
                shutil.rmtree(new_dir)
            old_dir.rename(new_dir)
        state.update(info["id"], source_kind="tiktok", status=st.DOWNLOADED, error=None, **info)
        print(f"    ✓ {short(info['caption'])}")
    return 0


def cmd_add(cfg: Config, state: State, args) -> int:
    for path in args.files:
        if not path.exists():
            print(f"  ✗ нет файла {path}")
            continue
        digest = hashlib.sha1(path.read_bytes()).hexdigest()[:10]
        video_id = f"local-{digest}"
        if video_id in state:
            print(f"  = {path.name} уже добавлен ({video_id})")
            continue
        dest = video_dir(cfg, video_id)
        dest.mkdir(parents=True, exist_ok=True)
        source = "source" + path.suffix.lower()
        shutil.copy2(path, dest / source)
        state.update(
            video_id,
            source_kind="local",
            status=st.DOWNLOADED,
            caption=args.caption or path.stem.replace("_", " "),
            upload_date=date.today().strftime("%Y%m%d"),
            source=source,
            subtitles=None,
        )
        print(f"  + {path.name} → {video_id}")
    return 0


def cmd_prepare(cfg: Config, state: State, args) -> int:
    from .video import check_ffmpeg, prepare

    check_ffmpeg()
    for video in state.with_status(st.DOWNLOADED)[: args.limit]:
        vdir = video_dir(cfg, video["id"])
        print(f"  ⚙ {video['id']}: {short(video.get('caption', ''))}")
        try:
            result = prepare(vdir / video["source"], vdir / "youtube.mp4", cfg.video)
        except (VideoError, OSError) as e:
            fail(state, video, e, st.DOWNLOADED)
            continue
        state.update(video["id"], status=st.PREPARED, error=None, **result)
        kind = "Shorts" if result["is_short"] else "обычное видео (длиннее 3 мин)"
        print(f"    ✓ {result['duration']} с, {kind}")
    return 0


def cmd_describe(cfg: Config, state: State, args) -> int:
    from .video import extract_frames

    if args.redo:
        videos = []
        for vid in args.redo:
            video = state.get(vid)
            if not video or video["status"] not in (st.PREPARED, st.DESCRIBED):
                print(f"  ✗ {vid}: нет такого подготовленного видео")
                continue
            videos.append(video)
    else:
        videos = state.with_status(st.PREPARED)[: args.limit]
    if not videos:
        return 0

    writer = None
    if cfg.meta.use_ai and not args.no_ai:
        try:
            writer = meta_mod.AIWriter(cfg.meta)
        except meta_mod.AIUnavailable as e:
            print(f"ИИ недоступен ({e}) — пишу описания по подписям из TikTok.")

    for video in videos:
        vdir = video_dir(cfg, video["id"])
        caption = video.get("caption", "")
        print(f"  ✎ {video['id']}: {short(caption)}")

        result = None
        if writer:
            recent = [
                v["title"]
                for v in state.with_status(st.DESCRIBED, st.UPLOADED, newest_first=True)
                if v.get("title") and v["id"] != video["id"]
            ][:10]
            subs = vdir / video["subtitles"] if video.get("subtitles") else None
            try:
                frames = extract_frames(vdir / "youtube.mp4", vdir / "frames", cfg.meta.frames)
                result = writer.write(
                    caption=caption,
                    transcript=meta_mod.read_subtitles(subs),
                    duration=video.get("duration") or 0,
                    frames=frames,
                    recent_titles=recent,
                )
            except meta_mod.AIUnavailable as e:
                print(f"    ИИ недоступен ({e}) — дальше по правилам.")
                writer = None
            except (RuntimeError, VideoError, ValueError, KeyError) as e:
                print(f"    ИИ не справился ({e}) — для этого видео по правилам.")
        if result is None:
            result = meta_mod.rule_based(caption, cfg.meta)

        final = meta_mod.finalize(result, cfg.meta, video.get("is_short", True))
        (vdir / "youtube.txt").write_text(meta_mod.to_text(final), encoding="utf-8")
        state.update(
            video["id"],
            status=st.DESCRIBED,
            error=None,
            title=final.title,
            description=final.description,
            tags=final.tags,
            meta_source=final.source,
        )
        print(f"    ✓ {final.title}")
    return 0


def cmd_upload(cfg: Config, state: State, args) -> int:
    from .youtube import QuotaExceeded, YouTubeError, get_service, next_slots, upload

    limit = min(args.limit or cfg.youtube.max_uploads_per_run, cfg.youtube.max_uploads_per_run)
    newest_first = cfg.youtube.order == "newest"
    batch = state.with_status(st.DESCRIBED, newest_first=newest_first)[:limit]
    if not batch:
        print("Нет видео, готовых к загрузке.")
        return 0

    slots: list[str | None] = [None] * len(batch)
    if cfg.youtube.schedule:
        taken = {v["publish_at"] for v in state.with_status(st.UPLOADED) if v.get("publish_at")}
        slots = next_slots(taken, cfg.youtube.times, cfg.youtube.timezone, len(batch))

    if args.dry_run:
        for video, slot in zip(batch, slots):
            print(f"  [проверка] {video['id']}: {video['title']}" + (f" → {slot}" if slot else ""))
        return 0

    try:
        service = get_service(cfg)
    except YouTubeError as e:
        print(f"Не удалось подключиться к YouTube: {e}")
        return 1

    for video, slot in zip(batch, slots):
        vdir = video_dir(cfg, video["id"])
        txt = vdir / "youtube.txt"
        try:
            final = meta_mod.from_text(txt.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            fail(state, video, f"youtube.txt: {e}", st.PREPARED)
            continue
        print(f"  ↑ {final.title}" + (f" (публикация {slot})" if slot else ""))
        try:
            yt_id = upload(service, vdir / "youtube.mp4", final, cfg, publish_at=slot)
        except QuotaExceeded as e:
            print(f"  ■ {e}")
            break
        except (YouTubeError, OSError) as e:
            fail(state, video, e, st.DESCRIBED)
            continue
        state.update(
            video["id"],
            status=st.UPLOADED,
            error=None,
            youtube_id=yt_id,
            publish_at=slot,
            title=final.title,
            description=final.description,
            tags=final.tags,
        )
        print(f"    ✓ https://youtu.be/{yt_id}")
    return 0


def cmd_run(cfg: Config, state: State, args) -> int:
    if cfg.tiktok.username:
        cmd_fetch(cfg, state, argparse.Namespace(url=None, links=None, limit=None))
    cmd_prepare(cfg, state, argparse.Namespace(limit=args.limit))
    cmd_describe(cfg, state, argparse.Namespace(limit=args.limit, redo=None, no_ai=args.no_ai))
    if args.no_upload:
        return cmd_status(cfg, state, args)
    if not cfg.path(cfg.youtube.client_secrets).exists():
        print(
            "\nYouTube API не подключён — готовые ролики лежат в data/videos/<id>/youtube.mp4, "
            "текст для них в youtube.txt рядом. Загрузите их вручную или подключите API (см. README)."
        )
        return cmd_status(cfg, state, args)
    cmd_upload(cfg, state, argparse.Namespace(limit=args.limit, dry_run=False))
    return cmd_status(cfg, state, args)


def cmd_status(cfg: Config, state: State, args) -> int:
    videos = list(state.videos.values())
    if not videos:
        print("Пока пусто. Начните с команды run.")
        return 0
    counts: dict[str, int] = {}
    for v in videos:
        counts[v["status"]] = counts.get(v["status"], 0) + 1
    print("\nВсего видео: " + str(len(videos)) + " — " + ", ".join(
        f"{st.STATUS_RU[s]}: {counts[s]}" for s in st.STATUS_RU if s in counts
    ))
    shown = sorted(videos, key=lambda v: v.get("upload_date") or "", reverse=True)
    shown = shown if getattr(args, "all", False) else shown[:15]
    for v in shown:
        line = f"  {v.get('upload_date') or '—':8}  {st.STATUS_RU[v['status']]:12}  {v['id']:20}  "
        line += short(v.get("title") or v.get("caption") or v.get("url") or "", 50)
        if v.get("youtube_id"):
            line += f"  https://youtu.be/{v['youtube_id']}"
        if v.get("publish_at"):
            line += f"  (публикация {v['publish_at']})"
        if v["status"] == st.FAILED:
            line += f"\n{'':36}{short(v.get('error') or '', 100)}"
        print(line)
    return 0


def cmd_skip(cfg: Config, state: State, args) -> int:
    for vid in args.ids:
        video = state.get(vid)
        if not video:
            print(f"  ✗ нет видео {vid}")
        elif video["status"] == st.UPLOADED:
            print(f"  ✗ {vid} уже на YouTube")
        else:
            back = video.get("retry_status") if video["status"] == st.FAILED else video["status"]
            state.update(vid, status=st.SKIPPED, retry_status=back)
            print(f"  – {vid} пропущено")
    return 0


def cmd_retry(cfg: Config, state: State, args) -> int:
    ids = args.ids or [v["id"] for v in state.with_status(st.FAILED)]
    for vid in ids:
        video = state.get(vid)
        if not video or video["status"] not in (st.FAILED, st.SKIPPED):
            print(f"  ✗ {vid}: не в статусе «ошибка» или «пропущено»")
            continue
        back = video.get("retry_status") or (
            st.DOWNLOADED if video.get("source") else st.NEW
        )
        state.update(vid, status=back, error=None)
        print(f"  ↺ {vid} → {st.STATUS_RU[back]}")
    return 0


# --- разбор аргументов -----------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tt2yt",
        description="Помощник канала: переносит ваши видео из TikTok на YouTube.",
    )
    parser.add_argument("-c", "--config", default="config.toml", help="файл настроек")
    sub = parser.add_subparsers(dest="command", required=True, metavar="команда")

    p = sub.add_parser("init", help="создать config.toml")
    p.add_argument("--username", help="ник в TikTok")

    p = sub.add_parser("run", help="всё сразу: скачать → подготовить → описать → загрузить")
    p.add_argument("--limit", type=int, help="не больше N видео на каждом шаге")
    p.add_argument("--no-upload", action="store_true", help="не загружать на YouTube")
    p.add_argument("--no-ai", action="store_true", help="описания без ИИ")

    p = sub.add_parser("fetch", help="скачать новые видео из TikTok")
    p.add_argument("--url", action="append", help="ссылка на конкретное видео (можно несколько)")
    p.add_argument("--links", type=Path, help="файл со ссылками, по одной на строку")
    p.add_argument("--limit", type=int)

    p = sub.add_parser("add", help="добавить видеофайлы с компьютера")
    p.add_argument("files", nargs="+", type=Path)
    p.add_argument("--caption", default="", help="подпись/тема видео для описания")

    p = sub.add_parser("prepare", help="перекодировать для YouTube Shorts")
    p.add_argument("--limit", type=int)

    p = sub.add_parser("describe", help="написать название, описание и теги")
    p.add_argument("--limit", type=int)
    p.add_argument("--redo", nargs="+", metavar="ID", help="переписать описание для этих видео")
    p.add_argument("--no-ai", action="store_true")

    p = sub.add_parser("upload", help="загрузить на YouTube")
    p.add_argument("--limit", type=int)
    p.add_argument("--dry-run", action="store_true", help="только показать, что будет загружено")

    p = sub.add_parser("status", help="список видео и их состояние")
    p.add_argument("--all", action="store_true", help="показать все, а не последние 15")

    p = sub.add_parser("skip", help="не переносить эти видео")
    p.add_argument("ids", nargs="+", metavar="ID")

    p = sub.add_parser("retry", help="повторить видео с ошибкой (или пропущенные по ID)")
    p.add_argument("ids", nargs="*", metavar="ID")
    return parser


COMMANDS = {
    "run": cmd_run,
    "fetch": cmd_fetch,
    "add": cmd_add,
    "prepare": cmd_prepare,
    "describe": cmd_describe,
    "upload": cmd_upload,
    "status": cmd_status,
    "skip": cmd_skip,
    "retry": cmd_retry,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        return cmd_init(args)
    try:
        cfg = load_config(Path(args.config))
    except ConfigError as e:
        print(e)
        return 2
    state = State(cfg.data_dir / "state.json")
    try:
        return COMMANDS[args.command](cfg, state, args)
    except VideoError as e:
        print(e)
        return 1
    except KeyboardInterrupt:
        print("\nОстановлено. Прогресс сохранён — можно запустить снова.")
        return 130
