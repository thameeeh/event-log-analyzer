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
    def __init__(self,
                 event_number: int,
                 event_timestamp: str,
                 event_severity: EventSeverity,
                 object_name: str,
                 object_id: int,
                 event_id: int,
                 event_name: str,
                 event_description: str,
                 event_remedy: str,
                 event_readable: str,
                 event_raw: str
                 ) -> None:
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

    def summary(self) -> str:
        return (
            f"Event {self.event_number}, {self.event_timestamp}, "
            f"{self.event_severity.name}, {self.object_name}, {self.object_id}, "
            f"{self.event_id}, {self.event_name}, {self.event_description}, "
            f"{self.event_remedy}, {self.event_readable}, {self.event_raw}"
        )

    def __str__(self) -> str:
        return self.summary()

    def __repr__(self) -> str:
        return self.summary()


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

        row_list = []

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
    def __init__(self, events: list[Event]) -> None:
        self._events = events

    def filter_by_severity(self, min_severity: EventSeverity) -> list[Event]:
        """
        This function filters events by the chosen minimum severity
        :param min_severity: variable for the minimum severity
        :return: a list of events with severity at or above min_severity
        """
        event_list = []

        for one_event in self._events:
            if one_event.event_severity >= min_severity:
                event_list.append(one_event)

        return event_list

    def count_by_object(self) -> dict[str, int]:
        """
        This function counts the number of events by object name
        :return: a dictionary containing the object name and the count of events
        """
        event_dict = {}

        for one_event in self._events:
            if one_event.object_name not in event_dict:
                event_dict[one_event.object_name] = 1
            else:
                event_dict[one_event.object_name] += 1

        return event_dict

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
    def events(self):
        return self._events


if __name__ == "__main__":
    event = load_events(Path(__file__).parent / "event_log_sample.csv")
    log = EventLog(event)
    print(f"Loaded {len(event)} events")
    print(len(log.filter_by_severity(EventSeverity.ERROR)))
    print(log.count_by_object())
    print(log.error_rate)
    print(log.events)