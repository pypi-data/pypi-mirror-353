# srt-time-tweaker

**srt-time-tweaker** is a no-frills solution for fixing subtitle synchronization issues in SRT (SubRip Subtitle) files by precisely shifting all subtitle timestamps forward or backward using configurable time delays.

---

## Features

- Shift subtitle timestamps by specified hours, minutes, seconds, and milliseconds
- Accept delay as a single string in `HH:MM:SS,ms` format
- Supports adding or subtracting delay to/from timestamps
- Handles negative timing errors with an option to ignore or raise exceptions
- Usable both as a command-line tool and as a Python importable function

---

## Requirements

- Python 3.x

---

## Installation

```bash
pip install srt-time-tweaker
```

---

## Usage

### Command Line Interface (CLI)

Run `srt-time-tweaker` from the terminal to launch the program.

```bash
srt-time-tweaker INPUT_FILE [-o OUTPUT_FILE] [-H HOURS] [-M MINUTES] [-S SECONDS] [-ms MILLISECONDS] [-d DURATION] [--subtract] [--ignore-negative]
```

#### Arguments:

| Argument                | Description                                                                                        | Default      |
| ----------------------- | -------------------------------------------------------------------------------------------------- | ------------ |
| `INPUT_FILE`            | Path to input `.srt` subtitle file                                                                 | (required)   |
| `-o`, `--output`        | Path to output `.srt` file                                                                         | `output.srt` |
| `-H`, `--hours`         | Hours to shift                                                                                     | 0            |
| `-M`, `--minutes`       | Minutes to shift                                                                                   | 0            |
| `-S`, `--seconds`       | Seconds to shift                                                                                   | 0            |
| `-ms`, `--milliseconds` | Milliseconds to shift                                                                              | 0            |
| `-d`, `--duration`      | Time delay in `HH:MM:SS,ms` format (overrides hours, minutes, seconds, milliseconds)             | None         |
| `--subtract`            | Subtract the delay from timestamps instead of adding                                               | False        |
| `--ignore-negative`     | Ignore negative timing errors instead of raising exceptions (while subtract)                       | False        |

#### Examples:

Shift subtitles forward by 2 seconds:

```bash
srt-time-tweaker example.srt -S 2 -o shifted.srt
```

Shift subtitles backward by 1 minute 15 seconds:

```bash
srt-time-tweaker example.srt -M 1 -S 15 --subtract -o shifted_back.srt
```

Shift using duration string:

```bash
srt-time-tweaker example.srt -d 00:00:05,500 -o shifted_5s_500ms.srt
```

### Python API

Import and use `srt_time_tweaker` function directly in Python scripts.

```python
from srt_time_tweaker import srt_time_tweaker as srtt

srtt(
    srt_input="example.srt",
    srt_output="output.srt",
    hours=0,
    minutes=1,
    seconds=30,
    milliseconds=250,
    duration=None,                  # Override other time params if set (format: "HH:MM:SS,ms"); Default : None
    subtract_delay=False,           # True to subtract delay; Default : False
    ignore_negative_error=False     # Ignore negative timing errors instead of raising exceptions (while subtract); Default : False
)
```

#### Function Parameters

| Parameter               | Type   | Description                                                                                    | Default        |
| ----------------------- | ------ | ---------------------------------------------------------------------------------------------- | -------------- |
| `srt_input`             | `str`  | Path to input .srt subtitle file                                                               | (required)     |
| `srt_output`            | `str`  | Path to output .srt file                                                                       | `"output.srt"` |
| `hours`                 | `int`  | Hours to shift                                                                                 | 0              |
| `minutes`               | `int`  | Minutes to shift                                                                               | 0              |
| `seconds`               | `int`  | Seconds to shift                                                                               | 0              |
| `milliseconds`          | `int`  | Milliseconds to shift                                                                          | 0              |
| `duration`              | `str`  | Time delay in `HH:MM:SS,ms` format (overrides hours, minutes, seconds, milliseconds)           | None           |
| `subtract_delay`        | `bool` | Subtract the delay from timestamps instead of adding                                           | True           |
| `ignore_negative_error` | `bool` | Ignore negative timing errors instead of raising exceptions (while subtract)                   | False          |

---

## Example SRT

https://gist.github.com/BhagyaJyoti22006/d7b961e7a1c8b2a7708088cefd28749c

Click on the link and download the example.srt file with which the script can be tested however required.
Read the example.srt file to get an overall understanding about how they work.

---

## Notes

- If the delay subtracts more time than the original timestamp causing negative times, by default a `ValueError` is raised.
- Use `ignore_negative_error=True` to silently skip negative timing errors in codebase or pass `--ignore-negative` in CLI

---

## License

**Apache License 2.0**

This library is open-source and free to use under the [Apache 2.0 License](./LICENSE).

---

## Contributing

Contributions, suggestions, and feature requests are welcome! Feel free to submit an issue or PR.

---

## Author

Developed by [भाग्य ज्योति (Bhagya Jyoti)](https://github.com/BhagyaJyoti22006)

---

**Happy subtitle syncing!**

