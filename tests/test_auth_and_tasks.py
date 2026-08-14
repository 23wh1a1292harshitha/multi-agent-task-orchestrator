import uuid


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def register_and_login(client, email, password="TestPass123"):
    client.post("/auth/register", json={"email": email, "password": password})
    res = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    return res.json()["access_token"]


def test_register_creates_user(test_client):
    email = unique_email()
    res = test_client.post("/auth/register", json={"email": email, "password": "TestPass123"})
    assert res.status_code == 201
    assert res.json()["email"] == email
    assert "hashed_password" not in res.json()  # never leak the hash


def test_register_duplicate_email_fails(test_client):
    email = unique_email()
    test_client.post("/auth/register", json={"email": email, "password": "TestPass123"})
    res = test_client.post("/auth/register", json={"email": email, "password": "TestPass123"})
    assert res.status_code == 400


def test_login_with_wrong_password_fails(test_client):
    email = unique_email()
    test_client.post("/auth/register", json={"email": email, "password": "TestPass123"})
    res = test_client.post("/auth/login", data={"username": email, "password": "WrongPass"})
    assert res.status_code == 401


def test_login_returns_valid_token(test_client):
    email = unique_email()
    token = register_and_login(test_client, email)
    assert token is not None
    assert len(token) > 20


def test_create_task_requires_auth(test_client):
    res = test_client.post("/tasks", json={"input_text": "test task"})
    assert res.status_code == 401


def test_create_task_succeeds(test_client):
    email = unique_email()
    token = register_and_login(test_client, email)

    res = test_client.post(
        "/tasks",
        json={"input_text": "Research something"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    assert res.json()["status"] == "pending"


def test_get_own_task_succeeds(test_client):
    email = unique_email()
    token = register_and_login(test_client, email)

    create_res = test_client.post(
        "/tasks",
        json={"input_text": "Research something"},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = create_res.json()["id"]

    get_res = test_client.get(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_res.status_code == 200
    assert get_res.json()["id"] == task_id


def test_user_cannot_access_another_users_task(test_client):
    """This is the BOLA protection test — the most important one in this file."""
    user_a_email = unique_email()
    user_a_token = register_and_login(test_client, user_a_email)

    create_res = test_client.post(
        "/tasks",
        json={"input_text": "User A's private task"},
        headers={"Authorization": f"Bearer {user_a_token}"},
    )
    task_id = create_res.json()["id"]

    user_b_email = unique_email()
    user_b_token = register_and_login(test_client, user_b_email)

    res = test_client.get(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {user_b_token}"})
    assert res.status_code == 404  # not 403 — see Step 5's reasoning on existence leakage