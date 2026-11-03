import pytest
from starter import EventLog
from starter import EventSeverity
from starter import Event
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