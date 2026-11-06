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


def test_filter_by_severity_returns_empty_list_for_empty_log():
    log = EventLog([])
    actual = log.filter_by_severity(EventSeverity.WARNING)

    assert actual == []


def test_count_by_object_returns_empty_dict_for_empty_log():
    log = EventLog([])
    actual = log.count_by_object()

    assert actual == {}


def test_count_by_object(sample_events):

    log = EventLog(sample_events)
    result = log.count_by_object()
    assert result == {"Object A": 2, "Object B": 1}


def test_error_rate(sample_events):

    log = EventLog(sample_events)
    result = log.error_rate
    assert result == pytest.approx(1 / 3)


@pytest.fixture
def valid_log_data():
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

    with pytest.raises(ValueError, match=f"Missing fields"):
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