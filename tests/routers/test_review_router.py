from unittest.mock import patch


def test_review_success(client):
    with patch("routers.scripts.run_review") as mock_run_review:
        mock_run_review.return_value = "Looks solid, minor optimization possible."

        response = client.get("/v1/scripts/review/site/pages/home.groovy")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["path"] == "site/pages/home.groovy"
    assert body["review"] == "Looks solid, minor optimization possible."


def test_review_not_found_returns_404(client):
    with patch("routers.scripts.run_review", side_effect=FileNotFoundError("missing")):
        response = client.get("/v1/scripts/review/missing/path.groovy")

    assert response.status_code == 404


def test_review_unexpected_error_returns_500(client):
    with patch("routers.scripts.run_review", side_effect=RuntimeError("review error")):
        response = client.get("/v1/scripts/review/some/path.groovy")

    assert response.status_code == 500