"""Shared fixtures for analyzer tests"""
import pytest
from starter import EventSeverity

from tests.helpers import make_event

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
