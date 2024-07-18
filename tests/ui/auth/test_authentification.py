import pytest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
    )
)
from auth.authentification import authenticate_user, load_config


@pytest.fixture
def mock_st():
    with patch('auth.authentication.st') as mock:
        yield mock


@pytest.fixture
def mock_stauth():
    with patch('auth.authentication.stauth') as mock:
        yield mock


@pytest.fixture
def mock_yaml():
    with patch('auth.config.yaml') as mock:
        mock.load.return_value = {
            'credentials': {},
            'cookie': {'name': 'test', 'key': 'test', 'expiry_days': 30},
            'preauthorized': {}
        }
        yield mock


def test_load_config(mock_yaml):
    result = load_config()
    assert 'credentials' in result
    assert 'cookie' in result
    assert 'preauthorized' in result


def test_authenticate_user_success(mock_st, mock_stauth, mock_yaml):
    mock_authenticator = MagicMock()
    mock_authenticator.login.return_value = ('Test User', True, 'testuser')
    mock_stauth.Authenticate.return_value = mock_authenticator

    result = authenticate_user()

    assert result is True
    mock_st.sidebar.markdown.assert_called_with("Bienvenue, Test User ! 👋")


def test_authenticate_user_failure(mock_st, mock_stauth, mock_yaml):
    mock_authenticator = MagicMock()
    mock_authenticator.login.return_value = (None, False, None)
    mock_stauth.Authenticate.return_value = mock_authenticator

    result = authenticate_user()

    assert result is False
    mock_st.error.assert_called_with('Username/password is incorrect')
