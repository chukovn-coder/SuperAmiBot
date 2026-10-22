from handlers import routes
from forms.user import (
    bored,
    group_1,
    group_2,
    group_3,
    group_6,
)


def test_age_group_for_child():
    assert routes.get_age_group(10) == group_2


def test_age_group_for_teenager():
    assert routes.get_age_group(15) == group_3


def test_age_group_boundaries():
    assert routes.get_age_group(5) == group_1
    assert routes.get_age_group(100) == group_6


def test_invalid_age_has_no_group():
    assert routes.get_age_group(4) is None
    assert routes.get_age_group(101) is None


def test_child_cannot_get_restricted_activities(monkeypatch):
    selected = {}

    def fake_choice(activities):
        selected["activities"] = activities
        return activities[0]

    monkeypatch.setattr(routes, "choice", fake_choice)

    routes.get_random_activity("bored", bored, group_2)

    assert bored[14] not in selected["activities"]
    assert bored[18] not in selected["activities"]


def test_teenager_can_get_restricted_activities(monkeypatch):
    selected = {}

    def fake_choice(activities):
        selected["activities"] = activities
        return activities[0]

    monkeypatch.setattr(routes, "choice", fake_choice)

    routes.get_random_activity("bored", bored, group_3)

    assert bored[14] in selected["activities"]
    assert bored[18] in selected["activities"]
