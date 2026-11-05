import pytest
from starter import EventLog
from starter import EventSeverity
from starter import Event
from starter import load_events
from datetime import datetime


def make_event(
        number: int,
        severity: EventSeverity,
        object_name: str = "Object A",
    ) -> Event:
    return Event(
        number=number,
        timestamp=datetime(2026, 1, 1),
        severity=severity,
        object_name=object_name,
        object_id=10,
        id=100,
        name="Test",
        description="Testing event",
        remedy="",
        readable="",
        raw="",
    )


def test_empty_log_has_zero_error_rate():
    log = EventLog([])
    result = log.error_rate
    assert result == 0.0


@pytest.fixture
def sample_events():
    return [
        make_event(1, EventSeverity.INFO, object_name="Object A"),
        make_event(2, EventSeverity.WARNING, object_name="Object B"),
        make_event(3, EventSeverity.ERROR, object_name="Object A"),
    ]


@pytest.mark.parametrize(
    "min_severity, expected_numbers",
    [
        (EventSeverity.INFO, [1, 2, 3]),
        (EventSeverity.WARNING, [2, 3]),
        (EventSeverity.ERROR, [3]),
    ],
)


def test_filter_by_severity(
        sample_events, min_severity, expected_numbers
        ):

    log = EventLog(sample_events)
    result = log.filter_by_severity(min_severity)
    actual_numbers = [event.number for event in result]

    assert actual_numbers == expected_numbers


def test_count_by_object(sample_events):

    log = EventLog(sample_events)
    result = log.count_by_object()
    assert result == {"Object A": 2, "Object B": 1}


def test_error_rate(sample_events):

    log = EventLog(sample_events)
    result = log.error_rate
    assert result == pytest.approx(1 / 3)


@pytest.mark.parametrize(
    "prefix",
    [
        "",
        "sep=\t\n",
    ],
)
def test_load_events(prefix, tmp_path):
    file_path = tmp_path / "test.csv"

    headers = [
        "Event number", "Timestamp", "Severity",
        "Object name", "Object ID", "Event ID", "Event name",
        "Description", "Remedy", "Readable", "Raw",
    ]
    row = [
        "42", "2026-01-01 12:00:00", "Warning",
        "Object A", "10", "100", "Testing",
        "Test event", "", "", "",
    ]

    file_path.write_text(
        prefix
        + "\t".join(headers)
        + "\n"
        + "\t".join(row)
        + "\n"
    )

    actual = load_events(file_path)

    assert len(actual) == 1

    event = actual[0]

    assert event.number == 42
    assert event.timestamp == datetime(2026, 1, 1, 12, 0, 0)
    assert event.severity == EventSeverity.WARNING
    assert event.object_name == "Object A"
    assert event.name == "Testing"
    assert event.remedy == ""