import pytest
from app.io.csv_reader import CSVReader
from app.io.json_reader import JSONReader
from app.core.exceptions import DataFormatError



# CSVReader


class TestCSVReader:

    def test_reads_valid_csv(self, sample_csv):
        """CSVReader читает файл и возвращает генератор."""
        reader = CSVReader()
        rows = list(reader.read(sample_csv))  # конвертируем для теста
        assert len(rows) == 3

    def test_returns_dicts(self, sample_csv):
        """Каждый элемент результата — словарь."""
        reader = CSVReader()
        rows = list(reader.read(sample_csv))
        assert all(isinstance(r, dict) for r in rows)

    def test_raises_on_missing_file(self, tmp_path):
        """Несуществующий файл — DataFormatError."""
        reader = CSVReader()
        with pytest.raises(DataFormatError):
            list(reader.read(tmp_path / "nonexistent.csv"))

    def test_reads_headers_correctly(self, sample_csv):
        """Заголовки CSV становятся ключами словаря."""
        reader = CSVReader()
        rows = list(reader.read(sample_csv))
        assert "id" in rows[0]
        assert "amount" in rows[0]
        assert "category" in rows[0]
        assert "date" in rows[0]

    def test_empty_csv(self, tmp_path):
        """CSV только с заголовком — пустой результат."""
        p = tmp_path / "empty.csv"
        p.write_text("id,amount,category,date\n")
        reader = CSVReader()
        rows = list(reader.read(p))
        assert rows == []


# JSONReader
class TestJSONReader:

    def test_reads_valid_json(self, sample_json):
        """JSONReader читает файл и возвращает генератор."""
        reader = JSONReader()
        rows = list(reader.read(sample_json))
        assert isinstance(rows, list)
        assert len(rows) == 1

    def test_raises_on_missing_file(self, tmp_path):
        """Несуществующий файл — DataFormatError."""
        reader = JSONReader()
        with pytest.raises(DataFormatError):
            list(reader.read(tmp_path / "nonexistent.json"))

    def test_raises_on_non_list_json(self, tmp_path):
        """JSON-объект вместо списка — DataFormatError."""
        p = tmp_path / "bad.json"
        p.write_text('{"id": "1", "amount": 100}')
        reader = JSONReader()
        with pytest.raises(DataFormatError):
            list(reader.read(p))

    def test_raises_on_invalid_json(self, tmp_path):
        """Повреждённый JSON — DataFormatError."""
        p = tmp_path / "broken.json"
        p.write_text("{not valid json")
        reader = JSONReader()
        with pytest.raises(DataFormatError):
            list(reader.read(p))

    def test_empty_json_list(self, tmp_path):
        """Пустой список [] — валидно, возвращает []."""
        p = tmp_path / "empty.json"
        p.write_text("[]")
        reader = JSONReader()
        assert list(reader.read(p)) == []