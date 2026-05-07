import json
from pathlib import Path
from typing import List, Dict, Any

from app.io.base_reader import BaseReader
from app.core.exceptions import DataFormatError


class JSONReader(BaseReader):

    def read(self, path: Path) -> List[Dict[str, Any]]:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise DataFormatError("JSON must contain a list")

            return data

        except Exception as err:
            raise DataFormatError(f"JSON error in {path}: {err}") from err
