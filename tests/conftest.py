"""Shared fixtures for analyzer tests"""
import pytest
from starter import EventSeverity

from tests.helpers import make_event
from tests.helpers import write_log

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


@pytest.fixture(name="sample_events")
def fixture_sample_events():
    """
    Provide events with different severities and object names
    """
    return [
        make_event(1, EventSeverity.INFO, object_name="Object A"),
        make_event(2, EventSeverity.WARNING, object_name="Object B"),
        make_event(3, EventSeverity.ERROR, object_name="Object A"),
    ]


@pytest.fixture(name="log_with_invalid_row")
def fixture_log_with_invalid_row(tmp_path, valid_log_data):
    """
    Create a log with an invalid severity between two valid entries
    """
    file_path = tmp_path / "mixed_events.csv"
    headers, valid_row = valid_log_data

    rows = []

    for number, severity in [
        ("1", "Info"),
        ("2", "Critical"),
        ("3", "Warning"),
    ]:
        row = valid_row.copy()
        row[headers.index("Event number")] = number
        row[headers.index("Severity")] = severity

        rows.append(row)

    write_log(file_path, headers, rows)

    return file_path
