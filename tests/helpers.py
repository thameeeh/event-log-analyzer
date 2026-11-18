"""Helpers for creating test data"""
from datetime import datetime
from datetime import timedelta
from starter import Event, EventSeverity


def make_event(
            number: int,
            severity: EventSeverity,
            object_name: str = "Object A",
            name: str = "Test",
            timestamp: datetime = datetime(2026, 1, 1),
        ) -> Event:
    """
    Create an event with predictable test values
    """
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


def write_log(file_path, headers, rows):
    """
    write a tab-separated log for a test
    """
    lines = ["\t".join(headers)]

    for row in rows:
        lines.append("\t".join(row))

    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_bluetooth_events(actions):
    """
    Create Bluetooth events from action names and seconds after a fixed start
    """
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
