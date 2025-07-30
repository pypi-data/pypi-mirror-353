import argparse
import pathlib as pl
import sys
from .core import (
    sessions,
    export_markdown,
    export_html,
    export_csv,
    export_json,
    export_sqlite
)

def main() -> None:
    """Command-line interface for grok-export-viewer."""
    p = argparse.ArgumentParser(
        description="Convert Grok Chat export JSON to various formats."
    )
    p.add_argument(
        "-s",
        "--source",
        default="data/prod-grok-backend.json",
        help="Path to Grok exported JSON"
    )
    p.add_argument(
        "-f",
        "--format",
        choices=["md", "html", "csv", "json", "sqlite"],
        default="html",
        help="Output format (default: html)"
    )
    args = p.parse_args()

    src = pl.Path(args.source)
    try:
        if not src.exists():
            sys.exit(f"❌ Source file not found: {src}")
        conv = sessions(src)
        if not conv:
            sys.exit("❌ No conversations found in the JSON file")
    except ValueError as e:
        sys.exit(f"❌ Error: {e}")

    match args.format:
        case "md":
            export_markdown(conv)
        case "html":
            export_html(conv)
        case "csv":
            export_csv(conv)
        case "json":
            export_json(conv)
        case "sqlite":
            export_sqlite(conv)

if __name__ == "__main__":
    main()