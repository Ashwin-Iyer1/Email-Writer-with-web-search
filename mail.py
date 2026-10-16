"""Export a reviewed JSON contact list as unsent .eml drafts."""
import argparse
import json
from pathlib import Path
from contact_core import draft_archive

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contacts", type=Path)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("research-drafts.zip"))
    args = parser.parse_args()
    data = draft_archive(json.loads(args.contacts.read_text(encoding="utf-8")), args.subject, args.body_file.read_text(encoding="utf-8"))
    with args.output.open("xb") as handle:
        handle.write(data)
    print(f"Saved {args.output}; no messages sent.")

if __name__ == "__main__":
    main()
