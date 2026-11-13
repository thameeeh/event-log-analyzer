# Event Log Analyzer

The analyzer loads event logs, filters events by severity, counts events by object, 
calculates the error rate and reports a BLUETOOTH session length

## Run the analyzer

Tested in Python 3.14.8
In the repository root run the following:

```
python "python task/starter.py" "path/to/your-log.csv"
```
Replace `path/to/your-log.csv` with an actual path to a log file.

Or run it from `gui.py`:

```
python "python task/gui.py"
```
Select your log file in the window that opens, then follow the prompts in the terminal.

## Handling invalid rows

By default, `starter.py` stops when it encounters an invalid event row.

Use `--skip-invalid` to skip malformed rows anda continue loading:

```powershell
python "python task/starter.py" "path/to/your-log.csv" --skip-invalid
```
Each skipped row produces a warning containing the filename, data-row number and reason.
Data-row numbering starts at 1 and excludes the header and optional `sep=` line

Statistics are calculated from the successfully loaded events

File-level problems such as missing headers or an invalid delimiter declaration still stop loading.

## Input format

The log must contain ALL 11 headers below. They can appear in any order:
"Event number", "Timestamp", "Severity", "Object name",
"Object ID", "Event ID", "Event name","Description",
"Remedy", "Readable", "Raw"

Without them all, the analyzer will throw errors about missing headers.

The "Timestamp" column uses `YYYY-MM-DD HH:MM:SS`, for example `2026-01-01 12:00:00`.
The "Severity" column accepts Info, Warning or Error.
The "Event number", "Object ID", "Event ID" columns must be integers.

Save the log as UTF-8. The analyzer uses tabs by default.
An optional first line beginning with sep= can specify a single-character delimiter.
For example, sep=, tells the analyzer to use commas.
The header row follows that line.

## Development

The analyzer uses Python’s standard library. To run the development checks,
activate a virtual environment and install the tools below.

```
python -m pip install -r requirements.txt
python -m pip install pytest-cov pylint
```

This runs the test suite and gives a coverage report:
```
python -m pytest "python task/test_starter.py"
python -m pytest "python task/test_starter.py" --cov=starter --cov-branch --cov-report=term-missing
```

This lints the files.
```
python -m pylint "python task/starter.py" "python task/test_starter.py"
```