# subtitle-workbench

Convert basic SRT and WebVTT subtitles and shift their timestamps. Output is written to a new file.

## Status

Initial prototype, created in October 2026. This is a small,
independent starter project, without claims of production deployment or adoption.

## Installation

Python 3.10+ is required. No third-party Python packages are needed.
Copy this directory, then run commands from inside it.

## Usage

```sh
python3 cli.py examples/demo.srt --output demo.vtt --format vtt --shift-ms 500
```

Run `python3 cli.py --help` for options. Reports go to standard output unless an
output file is specified. Input errors return status 2.

## Limitations

Supports plain cues only. VTT cue settings are rejected; NOTE/STYLE/REGION metadata and cue identifiers are discarded. Does not transcribe, translate or merge subtitles.

## Development and contributing

Keep changes narrowly scoped. Include a reproducible example for a bug report.
Use synthetic fixtures rather than personal, proprietary or research data.
Run the project checks from this directory:

```sh
python3 -m unittest discover -s tests -v
```

## License

MIT; see [LICENSE](LICENSE).
