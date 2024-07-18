import pytest
from unittest.mock import patch
import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
    )
)
from app import main


@pytest.fixture
def mock_st():
    with patch('app.st') as mock:
        yield mock


@pytest.fixture
def mock_authenticate_user():
    with patch('app.authenticate_user') as mock:
        yield mock


@pytest.fixture
def mock_render_navigation():
    with patch('app.render_navigation') as mock:
        yield mock


@pytest.fixture
def mock_render_home():
    with patch('app.render_home') as mock:
        yield mock


def test_main_authenticated(
        mock_st,
        mock_authenticate_user,
        mock_render_navigation,
        mock_render_home
):
    mock_authenticate_user.return_value = True
    mock_render_navigation.return_value = "Home"

    main()

    mock_authenticate_user.assert_called_once()
    mock_render_navigation.assert_called_once()
    mock_render_home.assert_called_once()


def test_main_not_authenticated(mock_st, mock_authenticate_user):
    mock_authenticate_user.return_value = False

    main()

    mock_authenticate_user.assert_called_once()
    mock_st.error.assert_not_called()
