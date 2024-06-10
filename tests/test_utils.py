import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scr.utils import extract_text_from_pdf, ModelError
from unittest.mock import patch, MagicMock


def test_extract_text_from_pdf():
    with patch("scr.utils.extract_text") as mock_extract:
        mock_extract.return_value = "Dummy text from PDF"
        result = extract_text_from_pdf("dummy_path.pdf")
        assert result == "Dummy text from PDF"

def test_model_error():
    with pytest.raises(ModelError):
        raise ModelError("This is a test error")
