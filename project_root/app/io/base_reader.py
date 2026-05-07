from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any


class BaseReader(ABC):

    @abstractmethod
    def read(self, path: Path) -> List[Dict[str, Any]]:
        pass
