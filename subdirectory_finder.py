"""Extract contacts from a saved page without opening browsers or sending mail."""
import argparse
import json
from pathlib import Path
from contact_core import extract_contacts

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page", type=Path)
    parser.add_argument("--url", required=True)
    parser.add_argument("--organization", default="")
    args = parser.parse_args()
    print(json.dumps(extract_contacts(args.page.read_text(encoding="utf-8"), args.url, args.organization), indent=2))

if __name__ == "__main__":
    main()
