"""Tests for event loading, analysis and command-line behavior"""
# Test names describe the behavior of the test
# pylint: disable=missing-function-docstring

import sys
import runpy

from datetime import datetime
from datetime import timedelta
from starter import EventLog
from starter import EventSeverity
from starter import Event
from starter import load_events
from starter import main

import pytest


def make_event(
            number: int,
            severity: EventSeverity,
            name: str = "test",
            timestamp: datetime = datetime(2026, 1, 1),
            object_name: str = "Object A",
        ) -> Event:
    return Event(
        number=number,
        timestamp=timestamp,
        severity=severity,
        object_name=object_name,
        object_id=10,
        id=100,
        name=name,
        description="Testing event",
        remedy="",
        readable="",
        raw="",
    )


def make_bluetooth_events(actions):
    start = datetime(2026, 1, 1, 12, 0, 0)
    events = []

    for number, (name, seconds) in enumerate(actions, start=1):
        event = make_event(
            number=number,
            severity=EventSeverity.INFO,
            name=name,
            timestamp=start + timedelta(seconds=seconds),
            object_name="BLUETOOTH",
        )
        events.append(event)

    return events


def test_empty_log_has_zero_error_rate():
    log = EventLog([])
    result = log.error_rate
    assert result == 0.0


def test_events_property_returns_stored_events(sample_events):
    log = EventLog(sample_events)
    actual = log.events

    assert actual == sample_events


@pytest.mark.parametrize(
    "severity, expected_rate",
    [
        (EventSeverity.INFO, 0.0),
        (EventSeverity.WARNING, 0.0),
        (EventSeverity.ERROR, 1.0),
    ],
)


def test_error_rate_for_uniform_severity(
        severity, expected_rate
        ):
    log = EventLog([
        make_event(1, severity, object_name="Object A"),
        make_event(2, severity, object_name="Object B")
    ])

    actual = log.error_rate
    assert actual == pytest.approx(expected_rate)


@pytest.fixture(name="sample_events")
def fixture_sample_events():
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


def test_filter_by_severity_returns_empty_list_for_empty_log():
    log = EventLog([])
    actual = log.filter_by_severity(EventSeverity.WARNING)

    assert actual == []


def test_count_by_object_returns_empty_dict_for_empty_log():
    log = EventLog([])
    actual = log.count_by_object()

    # pylint: disable-next=use-implicit-booleaness-not-comparison
    assert actual == {}


def test_count_by_object(sample_events):

    log = EventLog(sample_events)
    result = log.count_by_object()
    assert result == {"Object A": 2, "Object B": 1}


def test_error_rate(sample_events):

    log = EventLog(sample_events)
    result = log.error_rate
    assert result == pytest.approx(1 / 3)


@pytest.fixture(name="valid_log_data")
def fixture_valid_log_data():
    """
    Return the column headers and one valid event row for loader tests
    """
    headers = [
        "Event number", "Timestamp", "Severity",
        "Object name", "Object ID", "Event ID", "Event name",
        "Description", "Remedy", "Readable", "Raw",
    ]
    row = [
        "42", "2026-01-01 12:00:00", "Warning",
        "Object A", "10", "100", "Testing",
        "Test event", "", "Readable", "Raw",
    ]

    return headers, row


@pytest.mark.parametrize(
    "prefix",
    [
        "",
        "sep=\t\n",
    ],
)


@pytest.mark.parametrize(
    "reverse_columns",
    [
        False,
        True,
    ],
)


def test_load_events(
        prefix, tmp_path, valid_log_data, reverse_columns
        ):
    file_path = tmp_path / "test.csv"

    headers, row = valid_log_data

    if reverse_columns:
        headers.reverse()
        row.reverse()

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
    assert event.object_id == 10
    assert event.id == 100
    assert event.description == "Test event"
    assert event.readable == "Readable"
    assert event.raw == "Raw"


def test_load_events_reads_multiple_rows(
        tmp_path, valid_log_data
        ):
    file_path = tmp_path / "test.csv"
    headers, row = valid_log_data

    second_row = row.copy()
    second_row[headers.index("Event number")] = "43"
    second_row[headers.index("Severity")] = "Error"

    content = (
        "\t".join(headers) + "\n"
        + "\t".join(row) + "\n"
        + "\t".join(second_row) + "\n"
    )

    file_path.write_text(content, encoding="utf-8")

    actual = load_events(file_path)

    assert len(actual) == 2
    assert [event.number for event in actual] == [42, 43]
    assert [event.severity for event in actual] == [
        EventSeverity.WARNING,
        EventSeverity.ERROR,
    ]


def test_load_events_rejects_empty_file(tmp_path):
    file_path = tmp_path / "test.csv"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="no column headers"):
        load_events(file_path)


def test_load_events_rejects_blank_headers(tmp_path):
    file_path = tmp_path / "test.csv"
    file_path.write_text("\t\t\n", encoding="utf-8")

    with pytest.raises(ValueError, match="no headers"):
        load_events(file_path)


def test_load_events_rejects_missing_file(tmp_path):
    file_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_events(file_path)


def test_load_events_rejects_unknown_severity(
        tmp_path, valid_log_data
):
    file_path = tmp_path / "test.csv"
    headers, row = valid_log_data

    severity_index = headers.index("Severity")
    row[severity_index] = "Critical"

    file_path.write_text(
        "\t".join(headers)
        + "\n"
        + "\t".join(row)
        + "\n"
    )

    with pytest.raises(ValueError, match="Unknown severity"):
        load_events(file_path)


@pytest.mark.parametrize(
    "column_name",
    [
        "Event number",
        "Object ID",
        "Event ID"
    ],
)


def test_load_events_rejects_invalid_integer(
        tmp_path, valid_log_data, column_name
        ):
    file_path = tmp_path / "test.csv"
    headers, row = valid_log_data

    column = headers.index(column_name)
    row[column] = "not a number"

    file_path.write_text(
        "\t".join(headers)
        + "\n"
        + "\t".join(row)
        + "\n"
    )

    with pytest.raises(ValueError):
        load_events(file_path)


def test_load_events_rejects_missing_header(
        tmp_path, valid_log_data
        ):
    file_path = tmp_path / "test.csv"
    headers, row = valid_log_data

    column = headers.index("Object ID")
    headers.pop(column)
    row.pop(column)

    file_path.write_text(
        "\t".join(headers)
        + "\n"
        + "\t".join(row)
        + "\n"
    )

    with pytest.raises(ValueError, match="Missing headers"):
        load_events(file_path)


def test_load_events_rejects_incomplete_row(
        tmp_path, valid_log_data
        ):
    file_path = tmp_path / "test.csv"
    headers, row = valid_log_data

    row.pop()

    file_path.write_text(
        "\t".join(headers)
        + "\n"
        + "\t".join(row)
        + "\n"
    )

    with pytest.raises(ValueError, match="Missing fields"):
        load_events(file_path)


@pytest.mark.parametrize(
    "prefix",
    [
        "sep=\n",
        "sep=||\t\n",
    ],
)


def test_load_events_rejects_invalid_delimiter(
        tmp_path, valid_log_data, prefix
        ):

    file_path = tmp_path / "test.csv"
    headers, row = valid_log_data

    file_path.write_text(
        prefix
        + "\t".join(headers)
        + "\n"
        + "\t".join(row)
    )

    with pytest.raises(ValueError, match="Invalid delimiter"):
        load_events(file_path)


@pytest.mark.parametrize(
    "timestamp",
    [
        "not-a-timestamp",
        "2026-02-60 12:03:28",
    ],
)


def test_load_events_rejects_invalid_timestamp(
        tmp_path, valid_log_data, timestamp
        ):
    file_path = tmp_path / "test.csv"
    headers, row = valid_log_data

    row[headers.index("Timestamp")] = timestamp

    file_path.write_text(
        "\t".join(headers)
        + "\n"
        + "\t".join(row)
        + "\n"
    )

    with pytest.raises(ValueError):
        load_events(file_path)


def test_main_reports_missing_file(tmp_path, monkeypatch, capsys):
    missing_path = tmp_path / "missing.csv"

    monkeypatch.setattr(
        sys,
        "argv",
        ["starter.py", str(missing_path)],
    )

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 1

    captured = capsys.readouterr()
    assert "Could not load the log:" in captured.out


def test_main_requires_file_path(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["starter.py"],
    )

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 2

    captured = capsys.readouterr().err
    assert "required: file_path" in captured


def test_main_loads_valid_file(
        tmp_path, monkeypatch, capsys, valid_log_data
        ):

    file_path = tmp_path / "test.csv"
    headers, row = valid_log_data

    file_path.write_text(
        "\t".join(headers)
        + "\n"
        + "\t".join(row)
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["starter.py", str(file_path)],
    )

    runpy.run_module("starter", run_name="__main__")

    output = capsys.readouterr().out
    assert "Loaded 1 events" in output
    assert "{'Object A': 1}" in output


def test_bluetooth_session_durations_for_one_session():
    events = make_bluetooth_events([
        ("CONNECT", 0),
        ("DISCONNECT", 150),
        ])

    log = EventLog(events)
    actual = log.bluetooth_session_durations()

    assert actual == [timedelta(seconds=150)]


def test_bluetooth_session_durations_for_multiple_disconnects():
    events = make_bluetooth_events([
        ("CONNECT", 0),
        ("DISCONNECT", 150),
        ("DISCONNECT", 360),
        ])

    log = EventLog(events)
    actual = log.bluetooth_session_durations()

    assert actual == [timedelta(seconds=150)]


def test_bluetooth_session_durations_for_multiple_connections():
    events = make_bluetooth_events([
        ("CONNECT", 0),
        ("CONNECT", 300),
        ("DISCONNECT", 360),
        ])

    log = EventLog(events)
    actual = log.bluetooth_session_durations()

    assert actual == [timedelta(seconds=60)]


def test_bluetooth_session_durations_for_multiple_good_connections():
    events = make_bluetooth_events([
        ("CONNECT", 0),
        ("DISCONNECT", 100),
        ("CONNECT", 300),
        ("DISCONNECT", 360),
        ])

    log = EventLog(events)
    actual = log.bluetooth_session_durations()

    assert actual == [
            timedelta(seconds=100),
            timedelta(seconds=60),
            ]

@pytest.mark.parametrize(
    "actions",
    [
        [],
        [("CONNECT", 0)],
        [("DISCONNECT", 0)],
        [("STATUS", 0)]
    ]
)


def test_no_complete_bluetooth_sessions(actions):
    events = make_bluetooth_events(actions)
    log = EventLog(events)
    actual = log.bluetooth_session_durations()

    # pylint: disable-next=use-implicit-booleaness-not-comparison
    assert actual == []


def test_unrelated_objects_events_dont_affect_bluetooth_session():
    events = make_bluetooth_events([
        ("CONNECT", 0),
        ("CONNECT", 60),
        ("DISCONNECT", 90),
        ("DISCONNECT", 120),
        ])

    events[1].object_name = "OTHER"
    events[2].object_name = "OTHER"

    log = EventLog(events)
    actual = log.bluetooth_session_durations()

    assert actual == [timedelta(seconds=120)]


def test_load_events_skips_invalid_row_when_enabled(
        valid_log_data, tmp_path
        ):

    file_path = tmp_path / "mixed_events.csv"
    headers, valid_row = valid_log_data

    content = "\t".join(headers) + "\n"

    for number, severity in [
        ("1", "Info"),
        ("2", "Critical"),
        ("3", "Warning"),
    ]:
        row = valid_row.copy()
        row[headers.index("Event number")] = number
        row[headers.index("Severity")] = severity

        content += "\t".join(row) + "\n"

    file_path.write_text(content, encoding="utf-8")

    actual = load_events(file_path, skip_invalid=True)

    assert [event.number for event in actual] == [1, 3]