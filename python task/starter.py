import argparse
from pathlib import Path
from enum import IntEnum
from datetime import datetime
from dataclasses import dataclass
from collections import Counter
import csv


class EventSeverity(IntEnum):
    INFO = 0
    WARNING = 1
    ERROR = 2

@dataclass
class Event:
    """
    The class event represents a single event in the event log
    """
    number: int
    timestamp: datetime
    severity: EventSeverity
    object_name: str
    object_id: int
    id: int
    name: str
    description: str
    remedy: str
    readable: str
    raw: str

    def __str__(self) -> str:
        return (
            f"Event {self.number}, {self.timestamp}, "
            f"{self.severity.name}, {self.object_name}, {self.object_id}, "
            f"{self.id}, {self.name}, {self.description}, "
            f"{self.remedy}, {self.readable}, {self.raw}"
        )

    def __repr__(self) -> str:
        return str(self)


def load_events(path: Path) -> list[Event]:
    """
    This function loads all events from the csv file and returns a list of those object events
    :param path: variable for the location of the file
    :return: a list of event objects
    """
    with open(path, "r", newline="") as file:
        first_line = file.readline().rstrip("\r\n")
        if first_line.startswith("sep="):
            delimiter = first_line.removeprefix("sep=")
            if len(delimiter) != 1:
                raise ValueError("Invalid delimiter")
        else:
            file.seek(0)
            delimiter = "\t"

        reader = csv.DictReader(file, delimiter=delimiter)

        headers = reader.fieldnames
        if not headers:
            raise ValueError("The file has no column headers. (Check if the file is empty)")

        if not any(header.strip() for header in headers):
            raise ValueError("The file has no headers")

        required_headers = ["Event number", "Timestamp", "Severity",
                            "Object name", "Object ID", "Event ID", "Event name",
                            "Description", "Remedy", "Readable", "Raw"]

        missing_headers = []

        for header in required_headers:
            if header not in headers:
                missing_headers.append(header)

        if missing_headers:
            missing_names = ", ".join(missing_headers)
            raise ValueError(f"Missing headers: {missing_names}")

        events = []

        for row in reader:

            missing_fields = []
            for header in required_headers:
                if row[header] is None:
                    missing_fields.append(header)

            if missing_fields:
                missing_names = ", ".join(missing_fields)
                raise ValueError(f"Missing fields: {missing_names}")

            severity_name = row["Severity"].upper()
            try:
                severity = EventSeverity[severity_name]
            except KeyError:
                raise ValueError(f"Unknown severity: {severity_name}")

            event = Event(
                number=int(row["Event number"]),
                timestamp = datetime.strptime(row["Timestamp"],
                                            "%Y-%m-%d %H:%M:%S"),
                severity = severity,
                object_name = row["Object name"],
                object_id = int(row["Object ID"]),
                id = int(row["Event ID"]),
                name = row["Event name"],
                description = row["Description"],
                remedy = row["Remedy"],
                readable = row["Readable"],
                raw = row["Raw"],
            )

            events.append(event)

    return events


class EventLog:
    def __init__(self, events: list[Event]) -> None:
        self._events = events

    def filter_by_severity(self, min_severity: EventSeverity) -> list[Event]:
        """
        This function filters events by the chosen minimum severity
        :param min_severity: variable for the minimum severity
        :return: a list of events with severity at or above min_severity
        """
        event_list = [one_event for one_event in self._events
                      if one_event.severity >= min_severity]

        return event_list

    def count_by_object(self) -> dict[str, int]:
        """
        This function counts the number of events by object name
        :return: a dictionary containing the object name and the count of events
        """
        object_names = [one_event.object_name for one_event in self._events]
        counts = Counter(object_names)

        return dict(counts)

    @property
    def error_rate(self) -> float:
        """
        This function calculates the error rate of the events log
        returns 0.0 if the log is empty.
        :return: the fraction of events that are errors
        """
        if not self._events:
            return 0.0

        total_events = len(self._events)
        error_events = len(self.filter_by_severity(EventSeverity.ERROR))

        error_fraction = error_events / total_events

        return error_fraction

    @property
    def events(self) -> list[Event]:
        return self._events


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read and analyze an event log."
    )
    parser.add_argument(
        "file_path",
        type=Path,
        help="Path to the event log",
    )
    args = parser.parse_args()
    file_path = args.file_path

    try:
        events = load_events(file_path)
    except (ValueError, OSError) as error:
        print(f"Could not load the log: {error}")
        raise SystemExit(1)

    log = EventLog(events)
    print(f"Loaded {len(events)} events")
    print(len(log.filter_by_severity(EventSeverity.ERROR)))
    print(log.count_by_object())
    print(log.error_rate)
    print(log.events)

if __name__ == "__main__":
    main()