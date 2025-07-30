# Grok Export Viewer

[![PyPI](https://img.shields.io/pypi/v/grok-export-viewer)](https://pypi.org/project/grok-export-viewer/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/your-username/grok-export-viewer/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/grok-export-viewer)](https://pypi.org/project/grok-export-viewer/)

Convert, browse, and search your **Grok Chat export** (`prod-grok-backend.json`) offline into **Markdown**, **HTML (with live search)**, **CSV**, **SQLite**, or **JSON**.

## Installation

```bash
pip install grok-export-viewer
```

## Usage

```bash
# Place your JSON file in data/
grok-export-viewer -s data/prod-grok-backend.json -f html
open data/html/index.html  # macOS (use xdg-open on Linux, start on Windows)

# Other formats: md, csv, json, sqlite
grok-export-viewer -s data/prod-grok-backend.json -f csv
```

## Features

- Convert Grok JSON exports to multiple formats.
- HTML output includes a searchable index.
- Lightweight and offline processing.
- Supports Python 3.8+.

## Development

```bash
git clone https://github.com/your-username/grok-export-viewer.git
cd grok-export-viewer
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[test]"
pytest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

MIT License. See [LICENSE](LICENSE) for details.
