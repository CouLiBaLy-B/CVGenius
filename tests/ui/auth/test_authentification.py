import pytest
from unittest.mock import patch, MagicMock, mock_open

from auth.authentification import authenticate_user, load_config


@pytest.fixture
def mock_st():
    with patch('auth.authentification.st') as mock:
        yield mock


@pytest.fixture
def mock_stauth():
    with patch('auth.authentification.stauth') as mock:
        yield mock


@pytest.fixture
def mock_yaml():
    with patch('builtins.open', mock_open(read_data="""
credentials: {}
cookie:
  name: "test"
  key: "test"
  expiry_days: 30
pre-authorized: {}
    """)), patch('auth.authentification.yaml.safe_load') as mock_yaml_load:
        mock_yaml_load.return_value = {
            'credentials': {},
            'cookie': {'name': 'test', 'key': 'test', 'expiry_days': 30},
            'pre-authorized': {}
        }
        yield mock_yaml_load


def test_load_config(mock_yaml):
    result = load_config()
    assert 'credentials' in result
    assert 'cookie' in result
    assert 'pre-authorized' in result


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
