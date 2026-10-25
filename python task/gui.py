from pathlib import Path
from textwrap import dedent
from tkinter import filedialog
from starter import EventLog, EventSeverity, load_events
import tkinter as tk
import argparse


def choose_file() -> Path | None:
    """
    Helper function for choosing a specific file to run through the system
    :return: returns an absolute path to a file or returns None if no file is selected
    """
    window = tk.Tk()
    window.withdraw()

    selected_path = filedialog.askopenfilename(
        parent=window,
        title="Choose event log file",
        filetypes=[
            ("Log files", "*.csv *.tsv"),
            ("All files", "*.*"),
        ]
    )

    window.destroy()

    if not selected_path:
        return None

    return Path(selected_path)


def show_menu() -> None:
    """
    Display to the user the available event log operations
    """
    menu = dedent("""
        Event log analyzer
        ------------------
        1. - Load a file
        2. - Show amount of events
        3. - Filter events by severity
        4. - Count by object name
        5. - Show error rate
        0. - exit
        """).strip()

    print(menu)


def main(path: Path) -> None:
    event = load_events(path)
    log = EventLog(event)

    while True:
        show_menu()
        user_input = input("What would you like to do?: ").strip()
        match user_input:
            case "0":
                return
            case "1":
                new_path = choose_file()

                if new_path is None:
                    print("Selection cancelled. Keeping the current log.")
                    continue

                new_events = load_events(new_path)
                log = EventLog(new_events)

                print(f"Loaded {len(new_events)} events from {new_path.name}.")
            case "2":
                print(f"Loaded {len(log.events)} events")
            case "3":
                severity_choice = input(
                    "Minimum severity (0=Info, 1=Warning, 2=Error): "
                ).strip()

                match severity_choice:
                    case "0":
                        severity_level = EventSeverity.INFO
                    case "1":
                        severity_level = EventSeverity.WARNING
                    case "2":
                        severity_level = EventSeverity.ERROR
                    case _:
                        print("Invalid severity. Choose 0, 1, or 2.")
                        continue

                matching_events = log.filter_by_severity(severity_level)

                if not matching_events:
                    print("No events match that minimum severity.")
                else:
                    for event in matching_events:
                        print(event)
            case "4":
                counted_by_name = log.count_by_object()
                for object_name, object_count in counted_by_name.items():
                    print(f"{object_name}: {object_count} events")
            case "5":
                error_rate = log.error_rate
                print(f"Error rate: {error_rate:.2%} or "
                      f"{error_rate}")
            case _:
                print("Unrecognized command: " + user_input)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read and analyze an event log."
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        type=Path,
        help="Path to the event log; opens a file picker if omitted",
    )
    args = parser.parse_args()
    file_path = args.file_path

    if file_path is None:
        file_path = choose_file()

    if file_path is None:
        print("No file path provided")
    else:
        main(file_path)

    #event = load_events(Path(__file__).parent / "event_log_sample.csv")
    #log = EventLog(event)
    #print(f"Loaded {len(event)} events")