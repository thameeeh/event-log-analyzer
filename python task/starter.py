"""
Load and analyze event logs from delimited text files
"""
import argparse
import logging
from pathlib import Path
from enum import IntEnum
from datetime import datetime
from datetime import timedelta
from dataclasses import dataclass
from collections import Counter
import csv


LOGGER = logging.getLogger(__name__)


class EventSeverity(IntEnum):
    """
    Event severity levels in increasing order
    """
    INFO = 0
    WARNING = 1
    ERROR = 2


# The event fields mirror the 11 columns in the log
@dataclass
class Event: # pylint: disable=too-many-instance-attributes
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


def read_delimiter(log_file):
    """
    Read the declared delimiter and leave the file positioned at the header.
    Default to a tab when there is no sep= declaration
    :param log_file: the file from load_events()
    :return: delimiter
    """
    first_line = log_file.readline().rstrip("\r\n")

    if first_line.startswith("sep="):
        delimiter = first_line.removeprefix("sep=")
        if len(delimiter) != 1:
            raise ValueError("Invalid delimiter")
    else:
        log_file.seek(0)
        delimiter = "\t"

    return delimiter


def event_from_row(row):
    """
    Build an event from a row with all required fields.
    :return: an event object
    """

    severity_name = row["Severity"].upper()
    try:
        severity = EventSeverity[severity_name]
    except KeyError as exc:
        raise ValueError(f"Unknown severity: {severity_name}") from exc

    event = Event(
        number=int(row["Event number"]),
        timestamp=datetime.strptime(row["Timestamp"],
                                    "%Y-%m-%d %H:%M:%S"),
        severity=severity,
        object_name=row["Object name"],
        object_id=int(row["Object ID"]),
        id=int(row["Event ID"]),
        name=row["Event name"],
        description=row["Description"],
        remedy=row["Remedy"],
        readable=row["Readable"],
        raw=row["Raw"],
    )

    return event


def load_events(path: Path, skip_invalid: bool = False) -> list[Event]:
    """
    This function loads all events from the csv file and returns a list of those object events
    :param skip_invalid: enabled means we skip malformed rows
    :param path: variable for the location of the file
    :return: a list of event objects
    """
    with open(path, "r", newline="", encoding="utf-8") as file:

        delimiter = read_delimiter(file)
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

        for row_number, row in enumerate(reader, start=1):

            try:
                missing_fields = []
                for header in required_headers:
                    if row[header] is None:
                        missing_fields.append(header)

                if missing_fields:
                    missing_names = ", ".join(missing_fields)
                    raise ValueError(f"Missing fields: {missing_names}")

                events.append(event_from_row(row))
            except ValueError as error:
                if not skip_invalid:
                    raise

                LOGGER.warning(
                    "Skipping data row %d in %s: %s",
                    row_number,
                    path.name,
                    error,
                )

    return events


class EventLog:
    """
    Filter and summarize a collection of loaded events
    """
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

    def bluetooth_session_durations(self) -> list[timedelta]:
        """
        Calculate the durations of completed Bluetooth sessions.
        Consecutive CONNECT events replace the pending start time.
        Only sessions closed by a DISCONNECT are included.
        :return: a list of timedelta objects
        """
        duration_list = []
        connection_started = None

        for one_event in self._events:
            if one_event.object_name == "BLUETOOTH":
                if one_event.name == "CONNECT":
                    connection_started = one_event.timestamp
                elif one_event.name == "DISCONNECT":
                    if connection_started is not None:
                        duration = one_event.timestamp - connection_started
                        duration_list.append(duration)
                        connection_started = None

        return duration_list

    @property
    def error_rate(self) -> float:
        """
        Return the fraction of events at ERROR or higher, or 0.0 for an empty log
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
        """
        This function returns the stored event list
        :return: stored event list
        """
        return self._events


def main() -> None:
    """
    Load a log from a command-line path and print its statistics and events
    """
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
        raise SystemExit(1) from error

    log = EventLog(events)
    print(f"Loaded {len(events)} events")
    print(len(log.filter_by_severity(EventSeverity.ERROR)))
    print(log.count_by_object())
    print(log.error_rate)
    print(log.events)
    print(log.bluetooth_session_durations())

if __name__ == "__main__":
    main()
