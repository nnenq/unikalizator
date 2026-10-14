"""Подготовка видео для YouTube Shorts с помощью ffmpeg."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .config import VideoConfig

# Вертикальные видео до 3 минут YouTube показывает как Shorts.
SHORTS_MAX_SECONDS = 180


class VideoError(Exception):
    pass


def check_ffmpeg() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise VideoError(
                f"Не найден {tool}. Установите ffmpeg (Windows: winget install Gyan.FFmpeg) "
                "и перезапустите терминал."
            )


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-15:])
        raise VideoError(f"{cmd[0]} завершился с ошибкой:\n{tail}")
    return result.stdout


def probe(path: Path) -> dict:
    out = _run([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(path),
    ])
    data = json.loads(out)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    return {
        "duration": float(data.get("format", {}).get("duration") or 0),
        "width": int(video["width"]) if video else 0,
        "height": int(video["height"]) if video else 0,
        "has_video": video is not None,
        "has_audio": has_audio,
    }


def prepare(src: Path, dst: Path, cfg: VideoConfig) -> dict:
    """Перекодирует в 9:16 H.264/AAC. Если исходник не вертикальный, по бокам
    будет размытая копия кадра вместо чёрных полос."""
    info = probe(src)
    if not info["has_video"]:
        raise VideoError("в файле нет видеодорожки")

    w, h = cfg.width, cfg.height
    vf = (
        f"[0:v]split=2[bg][fg];"
        f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=20:2[bgb];"
        f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease[fgs];"
        f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[v]"
    )
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", str(src),
        "-filter_complex", vf, "-map", "[v]",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(cfg.crf),
        "-map_metadata", "-1", "-movflags", "+faststart",
    ]
    if info["has_audio"]:
        cmd += ["-map", "0:a:0", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
        if cfg.normalize_audio:
            cmd += ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11"]
    else:
        cmd += ["-an"]

    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.stem + ".part" + dst.suffix)
    _run(cmd + [str(tmp)])
    tmp.replace(dst)

    duration = info["duration"]
    return {"duration": round(duration, 1), "is_short": duration <= SHORTS_MAX_SECONDS}


def extract_frames(src: Path, out_dir: Path, count: int) -> list[Path]:
    """Несколько кадров равномерно по видео — по ним ИИ поймёт, о чём ролик."""
    if count <= 0:
        return []
    duration = probe(src)["duration"]
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for i in range(count):
        t = duration * (i + 0.5) / count
        frame = out_dir / f"frame{i + 1}.jpg"
        _run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(src),
            "-frames:v", "1", "-vf", "scale=540:-2", "-q:v", "4", str(frame),
        ])
        if frame.exists():
            frames.append(frame)
    return frames
