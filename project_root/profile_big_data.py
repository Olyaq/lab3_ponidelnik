import tracemalloc
from pathlib import Path
from app.io.csv_reader import CSVReader
from app.services.validator import validate_record
from app.services.aggregator import Aggregator
from app.core.exceptions import BaseAppError

def main():
    path = Path(__file__).resolve().parent / "big_data.csv"

    if not path.exists():
        print("big_data.csv not found")
        return

    print(f"Processing {path.stat().st_size / 1024 / 1024:.0f} MB file...")

    tracemalloc.start()

    reader = CSVReader()
    aggregator = Aggregator(check_duplicates=False)  # без хранения id
    processed = 0

    for record in reader.read(path):
        try:
            tx = validate_record(record)
            aggregator.add(tx)
            processed += 1
        except BaseAppError:
            continue

    result = aggregator.summarize()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Processed rows: {processed:,}")
    print(f"Categories: {result}")
    print(f"Peak Memory Usage: {peak / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()
