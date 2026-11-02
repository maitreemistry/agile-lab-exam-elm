import pytest

from app import LeaveManager, create_app


@pytest.mark.parametrize(
    ("days", "approved", "balance"),
    [(2, True, 3), (5, True, 0), (6, False, 5)],
)
def test_leave_request_updates_balance(days, approved, balance):
    manager = LeaveManager({"Rushvi": 5})

    assert manager.request_leave("Rushvi", days) is approved
    assert manager.leaves_left("Rushvi") == balance


@pytest.mark.parametrize("days", [0, -1])
def test_leave_request_requires_positive_days(days):
    manager = LeaveManager({"Rushvi": 5})

    with pytest.raises(ValueError, match="positive"):
        manager.request_leave("Rushvi", days)


def test_login_success_shows_leave_balance():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "APP_USERNAME": "admin",
            "APP_PASSWORD": "leave123",
        }
    )
    client = app.test_client()

    response = client.post(
        "/login",
        data={"username": "admin", "password": "leave123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome, Rushvi." in response.data
    assert b"Leaves left: 5" in response.data

    response = client.post(
        "/request-leave",
        data={"days": "2"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Leave request approved for 2 day(s)." in response.data
    assert b"Leaves left: 3" in response.data


@pytest.mark.parametrize(
    ("username", "password"),
    [("wrong", "leave123"), ("admin", "wrong")],
)
def test_login_rejects_invalid_credentials(username, password):
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})
    client = app.test_client()

    response = client.post(
        "/login",
        data={"username": username, "password": password},
    )

    assert response.status_code == 401
    assert b"Invalid username or password." in response.data
