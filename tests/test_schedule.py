from datetime import datetime, timezone

from tt2yt.youtube import next_slots


def test_slots_skip_past_and_taken():
    now = datetime(2026, 10, 14, 10, 30, tzinfo=timezone.utc)  # 13:30 по Москве
    taken = {"2026-10-14T15:00:00Z"}  # 18:00 МСК сегодня уже занято
    slots = next_slots(taken, ["18:00", "12:00"], "Europe/Moscow", 3, now=now)
    assert slots == [
        "2026-10-15T09:00:00Z",
        "2026-10-15T15:00:00Z",
        "2026-10-16T09:00:00Z",
    ]


def test_slot_needs_an_hour_margin():
    now = datetime(2026, 10, 14, 8, 30, tzinfo=timezone.utc)  # 11:30 МСК
    assert next_slots(set(), ["12:00"], "Europe/Moscow", 1, now=now) == ["2026-10-15T09:00:00Z"]
