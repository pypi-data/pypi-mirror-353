

from mada_holidays import core


def test_get_holidays():
    holidays = core.get_holidays(2025)
    assert any("Fête de l'indépendance" in label for _, label in holidays)
    assert len(holidays) >= 7