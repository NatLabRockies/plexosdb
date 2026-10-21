"""Validate a PLEXOS XML model and save a plain-text report."""

import argparse
from pathlib import Path

from plexosdb import DatabaseValidationError, PlexosDB


def main() -> None:
    """Validate the requested XML model and write its findings to a text file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml_path", type=Path, help="PLEXOS model XML file")
    parser.add_argument("--output", type=Path, default=Path("validation_issues.txt"), help="Report path")
    args = parser.parse_args()
    db = PlexosDB.from_xml(args.xml_path)
    try:
        try:
            db.validate_database()
        except DatabaseValidationError as error:
            issues = "\n".join(
                f"- [{finding.category.value}] {finding.message}" for finding in error.findings
            )
            args.output.write_text(f"Database validation results:\n{issues}\n", encoding="utf-8")
            raise
        else:
            args.output.write_text("No validation issues found.\n", encoding="utf-8")
    finally:
        db._db.close()


if __name__ == "__main__":
    main()
