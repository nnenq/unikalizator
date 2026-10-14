from tt2yt.config import MetaConfig
from tt2yt.meta import (
    Meta, finalize, from_text, read_subtitles, rule_based, sanitize, split_caption, to_text,
)


def test_split_caption():
    text, tags = split_caption("Что скрывает Антарктида? #теории #fyp #антарктида")
    assert text == "Что скрывает Антарктида?"
    assert tags == ["теории", "fyp", "антарктида"]


def test_rule_based_drops_junk_hashtags():
    meta = rule_based("Тайна перевала Дятлова. Часть 2 #дятлов #fyp #рек #теории", MetaConfig())
    assert meta.title == "Тайна перевала Дятлова."
    assert meta.tags == ["дятлов", "теории"]
    assert "#fyp" not in meta.description


def test_rule_based_hashtags_only_caption():
    meta = rule_based("#бермудский_треугольник #fyp", MetaConfig())
    assert meta.title == "Бермудский треугольник"


def test_finalize_limits_and_shorts():
    cfg = MetaConfig(footer="Подпишись!", default_tags=["теории"])
    meta = finalize(Meta(title="«" + "очень " * 40 + "<длинное>»", description="Текст <b>", tags=["a"]), cfg, True)
    assert len(meta.title) <= 100
    assert "<" not in meta.title and ">" not in meta.title
    assert "<" not in meta.description
    assert meta.description.endswith("#shorts")
    assert "Подпишись!" in meta.description
    assert meta.tags == ["a", "теории"]


def test_finalize_long_video_has_no_shorts_tag():
    meta = finalize(Meta(title="Т", description="Д"), MetaConfig(), is_short=False)
    assert "#shorts" not in meta.description


def test_tags_total_length_limited():
    meta = sanitize(Meta(title="t", description="d", tags=[f"длинный тег номер {i}" for i in range(100)]))
    total = sum(len(t) + 3 for t in meta.tags)
    assert total <= 500
    assert len(meta.tags) == len({t.lower() for t in meta.tags})


def test_text_roundtrip_after_manual_edit():
    original = Meta(title="Тайна", description="Строка 1\n\nСтрока 2\n#shorts", tags=["теории", "тайны"])
    text = to_text(original).replace("Тайна", "Новая тайна").replace("тайны", "тайны, загадки")
    edited = from_text(text)
    assert edited.title == "Новая тайна"
    assert edited.description == original.description
    assert edited.tags == ["теории", "тайны", "загадки"]


def test_read_subtitles(tmp_path):
    vtt = tmp_path / "s.vtt"
    vtt.write_text(
        "WEBVTT\n\n1\n00:00:00.000 --> 00:00:01.000\nПривет\n\n"
        "2\n00:00:01.000 --> 00:00:02.000\nПривет\n\n"
        "3\n00:00:02.000 --> 00:00:03.000\n<c>это теория</c>\n",
        encoding="utf-8",
    )
    assert read_subtitles(vtt) == "Привет это теория"
    assert read_subtitles(tmp_path / "missing.vtt") == ""
