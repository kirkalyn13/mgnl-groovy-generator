from unittest.mock import patch


def test_generate_success(client):
    with patch("routers.scripts.run_generate") as mock_run_generate:
        mock_run_generate.return_value = {"script": "def foo() {}", "retries": 0}

        response = client.post("/v1/scripts/generate", json={
            "query": "fetch all pages",
            "workspaces": ["website"],
            "properties": ["title"],
            "allow_modifications": False,
        })

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["script"] == "def foo() {}"
    assert body["retries"] == 0


def test_generate_value_error_returns_400(client):
    with patch("routers.scripts.run_generate", side_effect=ValueError("bad query")):
        response = client.post("/v1/scripts/generate", json={
            "query": "not groovy related",
            "workspaces": [],
            "properties": [],
            "allow_modifications": False,
        })

    assert response.status_code == 400
    assert response.json()["detail"] == "bad query"


def test_generate_unexpected_error_returns_500(client):
    with patch("routers.scripts.run_generate", side_effect=RuntimeError("error")):
        response = client.post("/v1/scripts/generate", json={
            "query": "fetch pages",
            "workspaces": [],
            "properties": [],
            "allow_modifications": False,
        })

    assert response.status_code == 500
    assert response.json()["detail"] == "error"