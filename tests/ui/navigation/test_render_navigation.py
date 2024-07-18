import pytest
from unittest.mock import patch

from ui.navigation.render_navigation import render_navigation


@pytest.fixture
def mock_hc():
    with patch('ui.navigation.render_navigation.hc') as mock:
        yield mock


@pytest.fixture
def mock_get_over_theme():
    with patch('ui.navigation.render_navigation.get_over_theme') as mock:
        mock.return_value = {"some": "theme"}
        yield mock


@pytest.fixture
def mock_get_menu_data():
    with patch('ui.navigation.render_navigation.get_menu_data') as mock:
        mock.return_value = [{"id": "Test", "icon": "🏠", "label": "Test"}]
        yield mock


def test_render_navigation(mock_hc, mock_get_over_theme, mock_get_menu_data):
    result = render_navigation()

    mock_get_over_theme.assert_called_once()
    mock_get_menu_data.assert_called_once()
    mock_hc.nav_bar.assert_called_once_with(
        menu_definition=[{"id": "Test", "icon": "🏠", "label": "Test"}],
        override_theme={"some": "theme"},
        home_name="Home",
        hide_streamlit_markers=True,
        sticky_nav=True,
        sticky_mode="pinned",
    )
    assert result == mock_hc.nav_bar.return_value
