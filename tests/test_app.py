import pytest
from unittest.mock import patch

from app import main


# Mock Streamlit and other dependencies within the app module
@pytest.fixture
def mock_st():
    with patch('app.st') as mock:
        yield mock


@pytest.fixture
def mock_render_navigation():
    with patch('ui.navigation.render_navigation.render_navigation') as mock:
        yield mock


@pytest.fixture
def mock_render_home():
    with patch('ui.home.render_home.render_home') as mock:
        yield mock


@pytest.fixture
def mock_render_infos():
    with patch('ui.infos.render_infos.render_infos') as mock:
        yield mock


@pytest.fixture
def mock_render_todos():
    with patch('ui.todos.render_todos.render_todos') as mock:
        yield mock


@pytest.fixture
def mock_setup_page_config():
    with patch('configuration.config.setup_page_config') as mock:
        yield mock


@pytest.fixture
def mock_documentations():
    with patch('scr.documentation.documentations') as mock:
        yield mock


@pytest.fixture
def mock_authenticate_user():
    with patch('app.authenticate_user') as mock:
        yield mock


def test_main_authenticated(
        mock_st,
        mock_authenticate_user,
        mock_render_navigation,
        mock_render_home,
        mock_render_infos,
        mock_render_todos,
        mock_setup_page_config,
        mock_documentations
):
    mock_authenticate_user.return_value = True

    result = main(run_setup=False, test_mode=True)

    assert result is True
    mock_setup_page_config.assert_not_called()
    mock_authenticate_user.assert_called_once()
    mock_render_navigation.assert_not_called()
    mock_documentations.assert_not_called()
    mock_render_home.assert_not_called()
    mock_render_infos.assert_not_called()
    mock_render_todos.assert_not_called()


def test_main_not_authenticated(
        mock_st,
        mock_authenticate_user,
        mock_setup_page_config,
        mock_documentations
):
    mock_authenticate_user.return_value = False

    result = main(run_setup=False, test_mode=True)

    assert result is False
    mock_setup_page_config.assert_not_called()
    mock_authenticate_user.assert_called_once()
    mock_documentations.assert_not_called()
    mock_st.error.assert_not_called()
