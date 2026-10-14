from tt2yt.config import normalize_account
from tt2yt.research import build_report, competitors, fmt
from tt2yt.tiktok import select_popular


def test_normalize_account():
    assert normalize_account("https://www.tiktok.com/@toonstory10?_r=1&_t=ZS-9AYfB3Bv1DF") == "toonstory10"
    assert normalize_account("@ella.stewart8") == "ella.stewart8"
    assert normalize_account("quynh.hoa.can") == "quynh.hoa.can"


def entries(*views):
    return [{"id": str(i), "views": v} for i, v in enumerate(views)]


def test_select_popular_top_share():
    picked = select_popular(entries(10, 500, 30, 1000, None), top_share=0.4)
    assert [e["id"] for e in picked] == ["1", "3"]


def test_select_popular_min_views_and_default():
    assert len(select_popular(entries(10, 500, 30))) == 3
    assert [e["id"] for e in select_popular(entries(10, 500, 30), min_views=100)] == ["1"]
    assert select_popular([], top_share=0.5) == []


def test_fmt():
    assert fmt(1_100_000) == "1.1 млн"
    assert fmt(34_800) == "34.8 тыс"
    assert fmt(2_000) == "2 тыс"
    assert fmt(999) == "999"
    assert fmt(None) == "—"


def test_competitors_and_report():
    results = [
        {"query": "q1", "title": "A", "url": "u1", "views": 100, "channel": "Кан1", "channel_url": "c1"},
        {"query": "q2", "title": "B", "url": "u2", "views": 900, "channel": "Кан1", "channel_url": "c1"},
        {"query": "q1", "title": "C", "url": "u3", "views": 500, "channel": "Кан2", "channel_url": "c2"},
    ]
    chans = competitors(results)
    assert [c["channel"] for c in chans] == ["Кан1", "Кан2"]
    assert chans[0]["views"] == 1000 and chans[0]["hits"] == 2 and chans[0]["best"]["title"] == "B"

    account = [{"id": "1", "url": "t1", "caption": "Почему? #теории", "views": 300, "likes": 5}]
    report = build_report({"acc": (account, None), "bad": (None, "blocked")}, ["q1", "q2"], results, ["теории"])
    assert "### @acc" in report and "blocked" in report and "[Кан1](c1)" in report and "#теории" in report
