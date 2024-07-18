import pytest
from unittest.mock import patch, MagicMock

from configuration.config import (
    setup_page_config,
    get_over_theme,
    get_menu_data
)


@pytest.fixture
def mock_st():
    with patch('configuration.config.st') as mock:
        yield mock


@pytest.fixture
def mock_image():
    with patch('configuration.config.Image') as mock:
        mock_img = MagicMock()
        mock.open.return_value = mock_img
        yield mock


def test_setup_page_config(mock_st, mock_image):
    setup_page_config()

    mock_st.set_page_config.assert_called()
    mock_st.markdown.assert_called()


def test_get_over_theme():
    theme = get_over_theme()
    assert isinstance(theme, dict)
    assert "txc_inactive" in theme
    assert "color" in theme


def test_get_menu_data():
    menu_data = get_menu_data()
    assert isinstance(menu_data, list)
    assert len(menu_data) == 2
    assert all(isinstance(item, dict) for item in menu_data)
