"""Event Log Analyzer

Fill in the TODOs. Feel free to restructure anything here. this is just a starting point.
"""

from pathlib import Path


class EventSeverity:
    pass  # TODO


class Event:
    pass  # TODO


def load_events(path):
    pass  # TODO


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
