from pathlib import Path
import json
import logging

from app.io.csv_reader import CSVReader
from app.io.json_reader import JSONReader
from app.services.validator import validate_record
from app.services.aggregator import Aggregator
from app.core.exceptions import BaseAppError

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

READERS = {
    ".csv": CSVReader(),
    ".json": JSONReader(),
}


def main():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"

    if not data_dir.exists():
        logging.critical("Data directory not found")
        raise SystemExit(1)

    aggregator = Aggregator()

    total = 0
    success = 0
    errors = []

    for path in data_dir.iterdir():
        if not path.is_file():
            continue

        reader = READERS.get(path.suffix.lower())

        if not reader:
            logging.warning(f"Unsupported file: {path}")
            continue

        total += 1
        file_has_errors = False

        try:
            records = reader.read(path)

            for i, record in enumerate(records, start=1):
                try:
                    tx = validate_record(record)
                    aggregator.add(tx)
                except BaseAppError as err:
                    msg = f"{path.name} [row {i}]: {err}"
                    logging.error(msg)
                    errors.append(msg)
                    file_has_errors = True

        except BaseAppError as err:
            msg = f"{path.name}: {err}"
            logging.error(msg)
            errors.append(msg)
            file_has_errors = True

        except Exception:
            msg = f"{path.name}: unexpected error"
            logging.exception(msg)
            errors.append(msg)
            file_has_errors = True

        if not file_has_errors:
            success += 1

    result = aggregator.summarize()

    tmp_path = base_dir / "result.json.tmp"
    final_path = base_dir / "result.json"

    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    tmp_path.replace(final_path)

    print(f"\nProcessed: {total}")
    print(f"Success: {success}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("Error list:")
        for err in errors:
            print("-", err)

    print("Result saved to result.json")


if __name__ == "__main__":
    main()
