from unittest.mock import patch


def test_describe_success(client):
    with patch("routers.scripts.run_describe") as mock_run_describe:
        mock_run_describe.return_value = "This script fetches the homepage title."

        response = client.get("/v1/scripts/describe/site/pages/home.groovy")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["path"] == "site/pages/home.groovy"
    assert body["description"] == "This script fetches the homepage title."


def test_describe_not_found_returns_404(client):
    with patch("routers.scripts.run_describe", side_effect=FileNotFoundError("no such script")):
        response = client.get("/v1/scripts/describe/missing/path.groovy")

    assert response.status_code == 404


def test_describe_unexpected_error_returns_500(client):
    with patch("routers.scripts.run_describe", side_effect=RuntimeError("describe error")):
        response = client.get("/v1/scripts/describe/some/path.groovy")

    assert response.status_code == 500