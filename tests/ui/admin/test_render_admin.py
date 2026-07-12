import pytest
from unittest.mock import patch

from ui.admin.render_admin import render_admin


@pytest.fixture
def mock_st():
    with patch('ui.admin.render_admin.st') as mock:
        yield mock


@pytest.fixture
def mock_stauth():
    with patch('ui.admin.render_admin.stauth') as mock:
        mock.Hasher.return_value.generate.return_value = ['hashed-value']
        yield mock


@pytest.fixture
def mock_log_action():
    with patch('ui.admin.render_admin.log_action') as mock:
        yield mock


def test_render_admin_generates_secrets_snippet(mock_st, mock_stauth, mock_log_action):
    mock_st.form_submit_button.return_value = True
    mock_st.text_input.side_effect = ["jdupont", "Jean Dupont", "j.dupont@example.com", "temp-pass"]
    mock_st.selectbox.return_value = "recruiter"

    render_admin()

    mock_stauth.Hasher.assert_called_with(["temp-pass"])
    snippet = mock_st.code.call_args[0][0]
    assert "auth.credentials.usernames.jdupont" in snippet
    assert "hashed-value" in snippet
    assert "temp-pass" not in snippet
    mock_log_action.assert_called_once()


def test_render_admin_requires_all_fields(mock_st, mock_stauth, mock_log_action):
    mock_st.form_submit_button.return_value = True
    mock_st.text_input.side_effect = ["", "", "", ""]
    mock_st.selectbox.return_value = "recruiter"

    render_admin()

    mock_st.error.assert_called_with("Tous les champs sont obligatoires.")
    mock_stauth.Hasher.assert_not_called()
    mock_log_action.assert_not_called()
