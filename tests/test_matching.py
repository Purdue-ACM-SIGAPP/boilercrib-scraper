import pytest

from boilercrib_scraper.matching import (
    Matcher,
    SeedBuilding,
    load_aliases,
    load_seed,
    normalize,
)

# West Lafayette building names from housing.purdue.edu/data/room-rates.csv as of October 2026
CSV_BUILDINGS = [
    "3rd and West (UR Apts)",
    "Aspire Apartments",
    "Benchmark II (UR Apts)",
    "Blackbird Farms (UR Apts)",
    "Cary Quadrangle",
    "Earhart Hall",
    "First Street Towers",
    "Frieda Parker Hall",
    "Fuse (UR Apts)",
    "Grant 333 (UR Apts)",
    "Harrison Hall",
    "Hawkins Hall",
    "Hillenbrand Hall",
    "Hilltop Apartments",
    "Honors College Residences",
    "McCutcheon Hall",
    "Meredith Hall",
    "Meredith South",
    "Owen Hall",
    "Provenance (UR Apts)",
    "Russell 414 (UR Apts)",
    "Shreve Hall",
    "South Hall",
    "Steely 410 (UR Apts)",
    "Tarkington Hall",
    "Waldron 125 (UR Apts)",
    "Waldron 19 (UR Apts)",
    "Waldron Square (UR Apts)",
    "Wiley Hall",
    "Windsor Halls",
    "Winifred Parker Hall",
]


@pytest.fixture(scope="module")
def matcher() -> Matcher:
    return Matcher()


def names(buildings: list[SeedBuilding]) -> list[str]:
    return sorted(b.name for b in buildings)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Meredith Hall South", "meredith south"),
        ("Windsor Halls", "windsor"),
        ("Fuse (UR Apts)", "fuse"),
        ("Honors College and Residences North", "honors college north"),
        ("  Cary   Quadrangle ", "cary quadrangle"),
        ("3rd and West (UR Apts)", "3rd west"),
    ],
)
def test_normalize(raw: str, expected: str) -> None:
    assert normalize(raw) == expected


def test_seed_file_loads_all_buildings() -> None:
    seed = load_seed()

    assert len(seed) == 21
    assert all(b.id for b in seed)


def test_seed_names_stay_distinct_after_normalizing() -> None:
    seen: set[tuple[str, str]] = set()
    for b in load_seed():
        key = (b.building_type, normalize(b.name))

        assert key not in seen, f"{b.name} collides after normalizing"

        seen.add(key)


def test_wiley_hall_does_not_match_dining_court(matcher: Matcher) -> None:
    assert names(matcher.match("Wiley Hall")) == ["Wiley Hall"]
    assert names(matcher.match("Wiley")) == ["Wiley Hall"]


def test_dining_court_found_when_asked_for(matcher: Matcher) -> None:
    assert names(matcher.match("Wiley Dining Court", "DinningCourt")) == [
        "Wiley Dining Court"
    ]
    assert matcher.match("Wiley Dining Court") == []  # default is Housing only


def test_meredith_and_meredith_south_stay_separate(matcher: Matcher) -> None:
    assert names(matcher.match("Meredith Hall")) == ["Meredith Hall"]
    assert names(matcher.match("Meredith")) == ["Meredith Hall"]
    assert names(matcher.match("Meredith South")) == ["Meredith Hall South"]


def test_windsor_plural(matcher: Matcher) -> None:
    assert names(matcher.match("Windsor")) == ["Windsor Halls"]


def test_parker_halls(matcher: Matcher) -> None:
    assert names(matcher.match("Frieda Parker Hall")) == ["Frieda Parker Hall"]
    assert names(matcher.match("Winifred Parker Hall")) == ["Winifred Parker Hall"]


@pytest.mark.parametrize(
    "raw",
    ["Honors College Residences", "Honors College and Residences", "Honors College"],
)
def test_honors_college_maps_to_both_buildings(matcher: Matcher, raw: str) -> None:
    assert names(matcher.match(raw)) == [
        "Honors College and Residences North",
        "Honors College and Residences South",
    ]


def test_honors_north_and_south_still_match_individually(matcher: Matcher) -> None:
    assert names(matcher.match("Honors College and Residences North")) == [
        "Honors College and Residences North"
    ]


def test_aliases_only_point_at_real_seed_names() -> None:
    seed_names = {b.name for b in load_seed()}
    for targets in load_aliases().values():
        assert set(targets) <= seed_names


def test_bad_alias_is_rejected() -> None:
    with pytest.raises(ValueError, match="don't exist"):
        _ = Matcher(aliases={"x": ["Not A Real Hall"]})


def test_csv_buildings_report(matcher: Matcher) -> None:
    report = matcher.report(CSV_BUILDINGS)

    assert len(report.matched) == 17
    assert sorted(report.unmatched) == sorted(
        [
            "3rd and West (UR Apts)",
            "Aspire Apartments",
            "Benchmark II (UR Apts)",
            "Blackbird Farms (UR Apts)",
            "Fuse (UR Apts)",
            "Grant 333 (UR Apts)",
            "Hilltop Apartments",
            "Provenance (UR Apts)",
            "Russell 414 (UR Apts)",
            "South Hall",
            "Steely 410 (UR Apts)",
            "Waldron 125 (UR Apts)",
            "Waldron 19 (UR Apts)",
            "Waldron Square (UR Apts)",
        ]
    )


def test_typo_gets_a_suggestion_but_not_a_match(matcher: Matcher) -> None:
    report = matcher.report(["Tarkingtn Hall"])

    assert report.unmatched == ["Tarkingtn Hall"]
    assert "Tarkington Hall" in report.suggestions["Tarkingtn Hall"]
