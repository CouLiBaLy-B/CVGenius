import pytest
from unittest.mock import patch, MagicMock

from auth.authentification import (
    authenticate_user,
    load_config,
    get_user_role,
    is_admin,
    clear_sensitive_session_state,
)


SAMPLE_AUTH_SECRETS = {
    "auth": {
        "cookie": {"name": "test_cookie", "key": "test_key", "expiry_days": 1},
        "credentials": {
            "usernames": {
                "adminuser": {
                    "name": "Admin User",
                    "email": "admin@example.com",
                    "role": "admin",
                    "password": "hashed-admin",
                },
                "recruiter1": {
                    "name": "Recruiter One",
                    "email": "recruiter@example.com",
                    "role": "recruiter",
                    "password": "hashed-recruiter",
                },
            }
        },
        "pre-authorized": {"emails": []},
    }
}


@pytest.fixture
def mock_st():
    with patch('auth.authentification.st') as mock:
        mock.secrets = SAMPLE_AUTH_SECRETS
        mock.session_state = {}
        yield mock


@pytest.fixture
def mock_stauth():
    with patch('auth.authentification.stauth') as mock:
        yield mock


def test_load_config_reads_from_secrets(mock_st):
    config = load_config()

    assert set(config['credentials']['usernames']) == {'adminuser', 'recruiter1'}
    assert config['cookie']['name'] == 'test_cookie'
    assert config['pre-authorized'] == {'emails': []}


def test_get_user_role(mock_st):
    config = load_config()

    assert get_user_role(config, 'adminuser') == 'admin'
    assert get_user_role(config, 'recruiter1') == 'recruiter'
    assert get_user_role(config, 'someone_not_configured') == 'recruiter'


def test_authenticate_user_success_stores_username_and_role(mock_st, mock_stauth):
    mock_authenticator = MagicMock()
    mock_authenticator.login.return_value = ('Admin User', True, 'adminuser')
    mock_stauth.Authenticate.return_value = mock_authenticator

    result = authenticate_user()

    assert result is True
    assert mock_st.session_state['username'] == 'adminuser'
    assert mock_st.session_state['role'] == 'admin'


def test_authenticate_user_failure(mock_st, mock_stauth):
    mock_authenticator = MagicMock()
    mock_authenticator.login.return_value = (None, False, None)
    mock_stauth.Authenticate.return_value = mock_authenticator

    result = authenticate_user()

    assert result is False
    mock_st.error.assert_called_with('Username/password is incorrect')


def test_authenticate_user_pending_clears_sensitive_state(mock_st, mock_stauth):
    mock_st.session_state['offre'] = 'leftover job advert text'
    mock_authenticator = MagicMock()
    mock_authenticator.login.return_value = (None, None, None)
    mock_stauth.Authenticate.return_value = mock_authenticator

    result = authenticate_user()

    assert result is False
    assert 'offre' not in mock_st.session_state


def test_is_admin(mock_st):
    mock_st.session_state['role'] = 'admin'
    assert is_admin() is True

    mock_st.session_state['role'] = 'recruiter'
    assert is_admin() is False


def test_clear_sensitive_session_state_keeps_identity_keys(mock_st):
    mock_st.session_state.update({
        'offre': 'job advert text',
        'mail_resume': b'pdf-bytes',
        'consent_cv_job_offer': True,
        'username': 'adminuser',
        'role': 'admin',
    })

    clear_sensitive_session_state()

    assert 'offre' not in mock_st.session_state
    assert 'mail_resume' not in mock_st.session_state
    assert 'consent_cv_job_offer' not in mock_st.session_state
    assert mock_st.session_state['username'] == 'adminuser'
    assert mock_st.session_state['role'] == 'admin'
