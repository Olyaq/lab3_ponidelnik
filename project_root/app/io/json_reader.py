import json
from pathlib import Path
from typing import Generator, Dict, Any

from app.io.base_reader import BaseReader
from app.core.exceptions import DataFormatError


class JSONReader(BaseReader):

    def read(self, path: Path) -> Generator[Dict[str, Any], None, None]:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise DataFormatError("JSON must contain a list")

            for item in data:
                yield item          # отдаём один элемент за раз

        except DataFormatError:
            raise
        except Exception as err:
            raise DataFormatError(f"JSON error in {path}: {err}") from err