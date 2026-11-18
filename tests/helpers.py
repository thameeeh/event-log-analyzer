"""Helpers for creating test data"""
from datetime import datetime
from starter import Event, EventSeverity


def make_event(
            number: int,
            severity: EventSeverity,
            object_name: str = "Object A",
        ) -> Event:
    """
    Create an event with predictable test values
    """
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
