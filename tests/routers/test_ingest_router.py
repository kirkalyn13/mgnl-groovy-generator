from unittest.mock import patch, AsyncMock


def test_ingest_success(client):
    with patch("routers.scripts.run_ingest", new_callable=AsyncMock) as mock_run_ingest:
        mock_run_ingest.return_value = 5

        response = client.post("/v1/scripts/ingest", json={"path": "/data/scripts"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "5" in body["message"]


def test_ingest_unexpected_error_returns_500(client):
    with patch("routers.scripts.run_ingest", new_callable=AsyncMock, side_effect=RuntimeError("ingest error")):
        response = client.post("/v1/scripts/ingest", json={"path": "/data/scripts"})

    assert response.status_code == 500
    assert response.json()["detail"] == "ingest error"