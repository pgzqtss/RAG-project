import pytest
import os
import sys
from unittest.mock import patch
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utils.get_files import get_files  
@pytest.fixture
def mock_filesystem(tmp_path):
    """Creates a mock directory with files for testing."""
    test_dir = tmp_path / "files" / "1234"
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create sample files
    (test_dir / "file1.txt").write_text("Content 1")
    (test_dir / "file2.pdf").write_text("Content 2")

    return test_dir

@patch("os.listdir")
@patch("os.path.isfile")
@patch("os.path.abspath")  
def test_get_files(mock_abspath, mock_isfile, mock_listdir, mock_filesystem):
    """Test whether get_files correctly retrieves file paths."""
    mock_listdir.return_value = ["file1.txt", "file2.pdf"]
    mock_isfile.side_effect = lambda x: True  # Treat all as files

    mock_abspath.side_effect = lambda x: str(mock_filesystem)

    result = get_files(1234)

    assert isinstance(result, dict), f"Expected a dictionary but got {type(result)}: {result}"

    expected_files = {
        "file1": str(mock_filesystem / "file1.txt"),
        "file2": str(mock_filesystem / "file2.pdf"),
    }

    print("DEBUG: result =", result)
    print("DEBUG: expected_files =", expected_files)

    assert {k: Path(v).resolve() for k, v in result.items()} == {k: Path(v).resolve() for k, v in expected_files.items()}
