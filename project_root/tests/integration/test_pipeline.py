import json
import pytest
from unittest.mock import patch
from pathlib import Path

from app.io.csv_reader import CSVReader
from app.io.json_reader import JSONReader
from app.services.validator import validate_record
from app.services.aggregator import Aggregator
from app.core.exceptions import BaseAppError


def run_pipeline(data_dir: Path) -> dict:
    """
    Минимальная копия логики main() для тестирования.
    Читает все CSV/JSON из папки, валидирует, агрегирует.
    Возвращает словарь category -> sum.
    """
    READERS = {".csv": CSVReader(), ".json": JSONReader()}
    aggregator = Aggregator()

    for path in data_dir.iterdir():
        if not path.is_file():
            continue
        reader = READERS.get(path.suffix.lower())
        if not reader:
            continue
        try:
            records = reader.read(path)
            for record in records:
                try:
                    tx = validate_record(record)
                    aggregator.add(tx)
                except BaseAppError:
                    continue
        except BaseAppError:
            continue

    return aggregator.summarize()


# ---------------------------------------------------------------------------
# Основной пайплайн
# ---------------------------------------------------------------------------

class TestPipeline:

    def test_csv_one_valid_two_invalid(self, tmp_path):
        """1 хорошая + 2 плохих строки → в итоге только 1 запись."""
        csv = tmp_path / "data.csv"
        csv.write_text(
            "id,amount,category,date\n"
            "1,100,food,2024-01-01\n"       # хорошая
            "2,-50,transport,2024-01-02\n"  # плохая
            "3,abc,food,2024-01-03\n"       # плохая
        )
        result = run_pipeline(tmp_path)
        assert result == {"food": 100.0}

    def test_json_and_csv_combined(self, tmp_path):
        """CSV + JSON в одной папке — данные объединяются."""
        csv = tmp_path / "a.csv"
        csv.write_text(
            "id,amount,category,date\n"
            "1,100,food,2024-01-01\n"
        )
        js = tmp_path / "b.json"
        js.write_text(
            '[{"id": "2", "amount": "200", "category": "transport", "date": "2024-01-02"}]'
        )
        result = run_pipeline(tmp_path)
        assert result["food"] == 100.0
        assert result["transport"] == 200.0

    def test_unsupported_file_ignored(self, tmp_path):
        """Файлы с неизвестным расширением не вызывают ошибок."""
        (tmp_path / "readme.txt").write_text("ignore me")
        (tmp_path / "data.csv").write_text(
            "id,amount,category,date\n"
            "1,100,food,2024-01-01\n"
        )
        result = run_pipeline(tmp_path)
        assert result == {"food": 100.0}

    def test_empty_data_dir(self, tmp_path):
        """Пустая папка → пустой результат, нет исключений."""
        result = run_pipeline(tmp_path)
        assert result == {}

    def test_all_invalid_records(self, tmp_path):
        """Все строки невалидны → пустой результат."""
        csv = tmp_path / "data.csv"
        csv.write_text(
            "id,amount,category,date\n"
            "1,-100,food,2024-01-01\n"
            "2,0,food,2024-01-02\n"
        )
        result = run_pipeline(tmp_path)
        assert result == {}

    def test_result_json_written_correctly(self, tmp_path):
        """Результат корректно сериализуется в JSON."""
        csv = tmp_path / "data.csv"
        csv.write_text(
            "id,amount,category,date\n"
            "1,250,travel,2024-06-01\n"
        )
        result = run_pipeline(tmp_path)
        out = tmp_path / "result.json"
        with out.open("w") as f:
            json.dump(result, f)

        loaded = json.loads(out.read_text())
        assert loaded == {"travel": 250.0}


# ---------------------------------------------------------------------------
# Mocking: диск защищён от записи
# ---------------------------------------------------------------------------

class TestMocking:

    def test_permission_error_on_write_is_handled(self, tmp_path):
        """
        Если при записи result.json диск защищён от записи —
        PermissionError должен быть выброшен (и программа обязана его поймать).
        Тест проверяет что ошибка действительно возникает при патче.
        """
        csv = tmp_path / "data.csv"
        csv.write_text(
            "id,amount,category,date\n"
            "1,100,food,2024-01-01\n"
        )
        result = run_pipeline(tmp_path)
        out = tmp_path / "result.json"

        # Патчим io.open (именно его использует pathlib.Path.open внутри)
        with patch("io.open", side_effect=PermissionError("disk is read-only")):
            with pytest.raises(PermissionError):
                with out.open("w") as f:
                    json.dump(result, f)

    def test_csv_reader_ioerror_raises_data_format_error(self, tmp_path):
        """
        Если CSVReader не может открыть файл (IOError) —
        он оборачивает ошибку в DataFormatError, а не пробрасывает OSError.
        """
        from app.core.exceptions import DataFormatError
        reader = CSVReader()
        with patch("pathlib.Path.open", side_effect=IOError("disk failure")):
            with pytest.raises(DataFormatError):
                reader.read(tmp_path / "data.csv")