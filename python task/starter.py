"""Event Log Analyzer

Fill in the TODOs. Feel free to restructure anything here. this is just a starting point.
"""

from pathlib import Path
from enum import IntEnum
import csv


class EventSeverity(IntEnum):
    INFO = 0
    WARNING = 1
    ERROR = 2


class Event:
    """
    The class event represents a single event in the event log
    """
    def __init__(self, event_number: int, event_timestamp: str,
                 event_severity: EventSeverity, object_name: str, object_id: int,
                 event_id: int, event_name: str, event_description: str,
                 event_remedy: str, event_readable: str, event_raw: str):
        self.event_number = event_number
        self.event_timestamp = event_timestamp
        self.event_severity = event_severity
        self.object_name = object_name
        self.object_id = object_id
        self.event_id = event_id
        self.event_name = event_name
        self.event_description = event_description
        self.event_remedy = event_remedy
        self.event_readable = event_readable
        self.event_raw = event_raw

    def summary(self):
        return (
            f"Event {self.event_number}, {self.event_timestamp}, "
            f"{self.event_severity.name}, {self.object_name}, {self.object_id}, "
            f"{self.event_id}, {self.event_name}, {self.event_description}, "
            f"{self.event_remedy}, {self.event_readable}, {self.event_raw}"
        )

    def __str__(self):
        return self.summary()


def load_events(path):
    """
    This function loads all events from the csv file and returns a list of those object events
    :param path: variable for the location of the file
    :return: a list of event objects
    """
    with open(path, "r", newline="") as file:
        delimiter = file.readline().rstrip("\r\n").removeprefix("sep=")
        reader = csv.DictReader(file, delimiter=delimiter)
        row_list = []

        for row in reader:
            severity_name = row["Severity"].upper()
            severity = EventSeverity[severity_name]

            row_event = Event(
                event_number=int(row["Event number"]),
                event_timestamp = row["Timestamp"],
                event_severity = severity,
                object_name = row["Object name"],
                object_id = int(row["Object ID"]),
                event_id = int(row["Event ID"]),
                event_name = row["Event name"],
                event_description = row["Description"],
                event_remedy = row["Remedy"],
                event_readable = row["Readable"],
                event_raw = row["Raw"],
            )

            row_list.append(row_event)

    return row_list


class EventLog:
    def __init__(self, events):
        self._events = events

    def filter_by_severity(self, min_severity):
        pass  # TODO

    def count_by_object(self):
        pass  # TODO

    @property
    def error_rate(self):
        pass  # TODO


if __name__ == "__main__":
    events = load_events(Path(__file__).parent / "event_log_sample.csv")
    log = EventLog(events)
    print(f"Loaded {len(events)} events")
