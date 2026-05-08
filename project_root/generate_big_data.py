import csv
import random
import string
from pathlib import Path

CATEGORIES = ["food", "transport", "health", "entertainment", "travel"]
OUTPUT_PATH = Path(__file__).resolve().parent / "data" / "big_data.csv"


def random_date():
    year = random.randint(2020, 2024)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def generate(target_size_mb: int = 1000):
    print(f"Generating ~{target_size_mb} MB CSV...")

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "amount", "category", "date"])

        i = 0
        while OUTPUT_PATH.stat().st_size < target_size_mb * 1024 * 1024:
            writer.writerow([
                i,
                round(random.uniform(0.01, 99999.99), 2),
                random.choice(CATEGORIES),
                random_date(),
            ])
            i += 1

            if i % 500_000 == 0:
                mb = OUTPUT_PATH.stat().st_size / 1024 / 1024
                print(f"  {mb:.0f} MB written...")

    mb = OUTPUT_PATH.stat().st_size / 1024 / 1024
    print(f"Done. File size: {mb:.1f} MB, rows: {i:,}")


if __name__ == "__main__":
    generate()