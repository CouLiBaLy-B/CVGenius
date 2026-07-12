import pytest
from unittest.mock import patch

from ui.navigation.render_navigation import render_navigation


@pytest.fixture
def mock_st():
    with patch('ui.navigation.render_navigation.st') as mock:
        yield mock


@pytest.fixture
def mock_get_menu_data():
    with patch('ui.navigation.render_navigation.get_menu_data') as mock:
        mock.return_value = [{"id": "Infos", "icon": "💡", "label": "Infos"}]
        yield mock


@pytest.fixture
def mock_is_admin():
    with patch('ui.navigation.render_navigation.is_admin') as mock:
        mock.return_value = False
        yield mock


def test_render_navigation_includes_home_first(mock_st, mock_get_menu_data, mock_is_admin):
    render_navigation()

    mock_get_menu_data.assert_called_once_with(is_admin=False)
    args, kwargs = mock_st.radio.call_args
    assert args[1] == ["Home", "Infos"]
    assert kwargs["horizontal"] is True
    assert kwargs["key"] == "main_navigation"


def test_render_navigation_format_func_renders_icon_and_label(mock_st, mock_get_menu_data, mock_is_admin):
    render_navigation()

    _, kwargs = mock_st.radio.call_args
    assert kwargs["format_func"]("Home") == "🏠 Home"
    assert kwargs["format_func"]("Infos") == "💡 Infos"


def test_render_navigation_returns_selected_page(mock_st, mock_get_menu_data, mock_is_admin):
    mock_st.radio.return_value = "Infos"

    result = render_navigation()

    assert result == "Infos"
