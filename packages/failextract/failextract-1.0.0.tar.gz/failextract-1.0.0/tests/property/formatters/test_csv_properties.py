"""Property-based tests for CSV formatter."""

import csv
import io
import string
from datetime import datetime

from hypothesis import given
from hypothesis import strategies as st

from failextract import CSVFormatter

# Strategies for generating test data
text_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + " .,!?-_()[]{}",
    min_size=1,
    max_size=100,
)

identifier_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + "_", min_size=1, max_size=50
).filter(lambda x: x.isidentifier())

file_path_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + "_-", min_size=3, max_size=50
).map(lambda x: f"/test/{x}.py")

timestamp_strategy = st.datetimes(
    min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)
).map(lambda dt: dt.isoformat())

failure_data_strategy = st.fixed_dictionaries(
    {
        "timestamp": timestamp_strategy,
        "test_name": identifier_strategy,
        "test_module": identifier_strategy,
        "test_file": file_path_strategy,
        "test_source": text_strategy,
        "test_args": st.text(min_size=2, max_size=50),
        "test_kwargs": st.text(min_size=2, max_size=50),
        "exception_type": identifier_strategy,
        "exception_message": text_strategy,
        "exception_traceback": text_strategy,
        "extracted_code": st.lists(
            st.fixed_dictionaries(
                {
                    "file": file_path_strategy,
                    "function": identifier_strategy,
                    "line": st.integers(min_value=1, max_value=10000),
                    "source": text_strategy,
                }
            ),
            min_size=0,
            max_size=5,
        ),
    }
)


class TestCSVFormatterProperties:
    """Property-based tests for CSVFormatter."""

    @given(failures=st.lists(failure_data_strategy, min_size=0, max_size=10))
    def test_csv_structure_validity(self, failures):
        """Test that CSV formatter produces valid CSV."""
        formatter = CSVFormatter()
        result = formatter.format(failures)

        # Should parse as valid CSV
        csv_reader = csv.reader(io.StringIO(result))
        rows = list(csv_reader)

        # Should have header row
        assert len(rows) >= 1
        header = rows[0]
        assert "Test Name" in header
        assert "Exception Type" in header

        # Should have correct number of data rows
        data_rows = rows[1:]
        assert len(data_rows) == len(failures)

        # Each row should have same number of columns as header
        for row in data_rows:
            assert len(row) == len(header)

    @given(csv_special_chars=st.text(alphabet='",\n\r', min_size=1, max_size=20))
    def test_csv_character_handling(self, csv_special_chars):
        """Test CSV handling of special characters."""
        formatter = CSVFormatter()

        failure_data = {
            "test_name": f"test_csv{csv_special_chars}",
            "test_module": "test_module",
            "test_file": "/path/test.py",
            "timestamp": "2024-01-01T12:00:00",
            "exception_type": "ValueError",
            "exception_message": csv_special_chars,
            "extracted_code": [],
        }

        result = formatter.format([failure_data])

        # Should still be parseable CSV
        csv_reader = csv.reader(io.StringIO(result))
        rows = list(csv_reader)

        # Should have header + 1 data row
        assert len(rows) == 2

        # Data should be preserved (CSV parser handles escaping)
        data_row = rows[1]
        assert len(data_row) >= 2  # At least test name and exception type