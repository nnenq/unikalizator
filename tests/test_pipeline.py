"""Прогон по шагам на сгенерированном видео: add → prepare → describe → upload --dry-run."""

import json
import shutil
import subprocess

import pytest

from tt2yt.cli import main
from tt2yt.video import probe

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="нужен ffmpeg")


def make_video(path, size="1280x720", duration=3, audio=True):
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"testsrc=size={size}:rate=30:duration={duration}"]
    if audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}", "-shortest"]
    subprocess.run(cmd + [str(path)], check=True)


@pytest.fixture
def project(tmp_path):
    (tmp_path / "config.toml").write_text(
        '[tiktok]\nusername = ""\n[meta]\nuse_ai = false\nfooter = "Подпишись!"\n', encoding="utf-8"
    )
    return tmp_path


def run(project, *args):
    return main(["-c", str(project / "config.toml"), *args])


def state(project):
    return json.loads((project / "data" / "state.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("size,audio", [("1280x720", True), ("720x1280", False)])
def test_full_pipeline(project, tmp_path, size, audio, capsys):
    src = tmp_path / "Тайна_маяка.mp4"
    make_video(src, size=size, audio=audio)

    assert run(project, "add", str(src), "--caption", "Тайна старого маяка #теории #fyp") == 0
    assert run(project, "prepare") == 0
    (video,) = state(project).values()
    assert video["status"] == "prepared"
    assert video["is_short"] is True

    out = project / "data" / "videos" / video["id"] / "youtube.mp4"
    info = probe(out)
    assert (info["width"], info["height"]) == (1080, 1920)
    assert info["has_audio"] is audio

    assert run(project, "describe") == 0
    (video,) = state(project).values()
    assert video["status"] == "described"
    assert video["title"] == "Тайна старого маяка"
    assert "#shorts" in video["description"] and "Подпишись!" in video["description"]
    assert "теории" in video["tags"]

    capsys.readouterr()
    assert run(project, "upload", "--dry-run") == 0
    assert "Тайна старого маяка" in capsys.readouterr().out


def test_add_same_file_twice(project, tmp_path):
    src = tmp_path / "a.mp4"
    make_video(src, duration=1)
    run(project, "add", str(src))
    run(project, "add", str(src))
    assert len(state(project)) == 1


def test_skip_and_retry(project, tmp_path):
    src = tmp_path / "a.mp4"
    make_video(src, duration=1)
    run(project, "add", str(src))
    (vid,) = state(project)
    run(project, "skip", vid)
    assert state(project)[vid]["status"] == "skipped"
    run(project, "retry", vid)
    assert state(project)[vid]["status"] == "downloaded"
