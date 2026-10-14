"""Анализ: что набирает просмотры в ваших аккаунтах TikTok и кто похожие каналы на YouTube."""

from __future__ import annotations

import statistics
from collections import Counter
from datetime import date

import yt_dlp

from .meta import split_caption, useful_hashtags


def fmt(n: int | None) -> str:
    if n is None:
        return "—"
    for limit, suffix in ((1_000_000, " млн"), (1_000, " тыс")):
        if n >= limit:
            return f"{n / limit:.1f}".rstrip("0").rstrip(".") + suffix
    return str(n)


def top_hashtags(entries: list[dict], k: int = 5) -> list[str]:
    """Хэштеги самых просматриваемых видео — из них получаются запросы для поиска конкурентов."""
    counts: Counter[str] = Counter()
    for e in entries:
        _, tags = split_caption(e.get("caption", ""))
        for tag in useful_hashtags(tags):
            counts[tag.lower().replace("_", " ")] += (e.get("views") or 0) + 1
    return [tag for tag, _ in counts.most_common(k)]


class SearchError(Exception):
    pass


def youtube_search(query: str, count: int) -> list[dict]:
    opts = {"quiet": True, "noprogress": True, "extract_flat": "in_playlist", "skip_download": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch{count}:{query}", download=False)
    except yt_dlp.utils.DownloadError as e:
        raise SearchError(str(e).removeprefix("ERROR: ")) from e
    results = []
    for e in (info or {}).get("entries") or []:
        if not e:
            continue
        channel_url = e.get("channel_url") or (
            f"https://www.youtube.com/channel/{e['channel_id']}" if e.get("channel_id") else ""
        )
        results.append({
            "query": query,
            "title": e.get("title") or "",
            "url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
            "views": e.get("view_count"),
            "channel": e.get("channel") or e.get("uploader") or "?",
            "channel_url": channel_url,
        })
    return results


def competitors(results: list[dict]) -> list[dict]:
    """Каналы из выдачи, отсортированные по сумме просмотров найденных роликов."""
    channels: dict[str, dict] = {}
    for r in results:
        key = r["channel_url"] or r["channel"]
        c = channels.setdefault(key, {
            "channel": r["channel"], "url": r["channel_url"], "views": 0,
            "hits": 0, "queries": set(), "best": r,
        })
        c["views"] += r["views"] or 0
        c["hits"] += 1
        c["queries"].add(r["query"])
        if (r["views"] or 0) > (c["best"]["views"] or 0):
            c["best"] = r
    return sorted(channels.values(), key=lambda c: c["views"], reverse=True)


def account_section(account: str, entries: list[dict] | None, error: str | None) -> list[str]:
    lines = [f"### @{account}", ""]
    if error:
        return lines + [f"Не удалось получить видео: {error}", ""]
    views = [e["views"] for e in entries if e.get("views") is not None]
    median = int(statistics.median(views)) if views else None
    lines.append(
        f"Видео: {len(entries)}, медиана просмотров: {fmt(median)}, "
        f"всего: {fmt(sum(views) if views else None)}"
    )
    lines += ["", "| Просмотры | Лайки | Видео |", "|---:|---:|---|"]
    for e in sorted(entries, key=lambda e: e.get("views") or 0, reverse=True)[:10]:
        caption = " ".join(e["caption"].split())[:80].replace("|", "/") or "(без подписи)"
        mark = " 🔥" if median and (e.get("views") or 0) >= 3 * median else ""
        lines.append(f"| {fmt(e.get('views'))}{mark} | {fmt(e.get('likes'))} | [{caption}]({e['url']}) |")
    return lines + [""]


def build_report(
    accounts: dict[str, tuple[list[dict] | None, str | None]],
    queries: list[str],
    results: list[dict],
    hashtags: list[str] | None = None,
) -> str:
    lines = [f"# Анализ канала — {date.today():%d.%m.%Y}", ""]

    if accounts:
        lines += ["## Ваши аккаунты TikTok", "", "🔥 — видео, набравшее в 3+ раза больше медианы аккаунта.", ""]
        if hashtags:
            lines += ["Хэштеги самых просматриваемых видео: " + ", ".join(f"#{h}" for h in hashtags), ""]
        for account, (entries, error) in accounts.items():
            lines += account_section(account, entries, error)

    lines += ["## Похожие каналы на YouTube", "", "Запросы: " + ", ".join(f"«{q}»" for q in queries), ""]
    chans = competitors(results)
    if chans:
        lines += ["| Канал | Просмотры найденных роликов | Роликов в выдаче | Самый популярный ролик |", "|---|---:|---:|---|"]
        for c in chans[:20]:
            name = f"[{c['channel']}]({c['url']})" if c["url"] else c["channel"]
            best = c["best"]
            title = best["title"][:70].replace("|", "/")
            lines.append(f"| {name} | {fmt(c['views'])} | {c['hits']} | [{title}]({best['url']}) — {fmt(best['views'])} |")
    else:
        lines.append("Ничего не найдено.")

    lines += ["", "## Самые просматриваемые ролики по запросам", ""]
    for r in sorted(results, key=lambda r: r["views"] or 0, reverse=True)[:15]:
        lines.append(f"- {fmt(r['views'])} — [{r['title']}]({r['url']}) · {r['channel']}")
    return "\n".join(lines) + "\n"
