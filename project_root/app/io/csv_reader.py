import csv
from pathlib import Path
from typing import Generator, Dict, Any

from app.io.base_reader import BaseReader
from app.core.exceptions import DataFormatError


class CSVReader(BaseReader):

    def read(self, path: Path) -> Generator[Dict[str, Any], None, None]:
        try:
            with path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row          # отдаём одну строку за раз
        except Exception as err:
            raise DataFormatError(f"CSV error in {path}: {err}") from err