"""Unit tests for all API endpoints."""

from datetime import datetime, timedelta, timezone


class TestShorten:
    """POST /shorten"""

    def test_shorten_url(self, client):
        response = client.post("/shorten", json={"url": "https://example.com"})
        assert response.status_code == 201
        data = response.json()
        assert "short_code" in data
        assert "short_url" in data
        assert data["original_url"] == "https://example.com/"

    def test_shorten_with_custom_alias(self, client):
        response = client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_alias": "myalias"},
        )
        assert response.status_code == 201
        assert response.json()["short_code"] == "myalias"

    def test_shorten_duplicate_alias(self, client):
        client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_alias": "taken"},
        )
        response = client.post(
            "/shorten",
            json={"url": "https://other.com", "custom_alias": "taken"},
        )
        assert response.status_code == 409

    def test_shorten_with_expiry(self, client):
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        response = client.post(
            "/shorten",
            json={"url": "https://example.com", "expires_at": future},
        )
        assert response.status_code == 201

    def test_shorten_invalid_url(self, client):
        response = client.post("/shorten", json={"url": "not-a-url"})
        assert response.status_code == 422


class TestBulkShorten:
    """POST /shorten/bulk"""

    def test_bulk_shorten(self, client):
        response = client.post(
            "/shorten/bulk",
            json={
                "urls": [
                    {"url": "https://example.com"},
                    {"url": "https://google.com"},
                ]
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["results"]) == 2

    def test_bulk_shorten_with_alias_collision(self, client):
        response = client.post(
            "/shorten/bulk",
            json={
                "urls": [
                    {"url": "https://example.com", "custom_alias": "same"},
                    {"url": "https://google.com", "custom_alias": "same"},
                ]
            },
        )
        # Second alias collides with first
        assert response.status_code == 409


class TestRedirect:
    """GET /{short_code}"""

    def test_redirect(self, client):
        # Create a short URL first
        create_resp = client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_alias": "redir"},
        )
        assert create_resp.status_code == 201

        # Follow=False to catch the 302 instead of following it
        response = client.get("/redir", follow_redirects=False)
        assert response.status_code == 302
        assert "example.com" in response.headers["location"]

    def test_redirect_not_found(self, client):
        response = client.get("/nonexistent", follow_redirects=False)
        assert response.status_code == 404

    def test_redirect_expired(self, client):
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        client.post(
            "/shorten",
            json={
                "url": "https://example.com",
                "custom_alias": "expired",
                "expires_at": past,
            },
        )
        response = client.get("/expired", follow_redirects=False)
        assert response.status_code == 410


class TestStats:
    """GET /stats/{short_code}"""

    def test_stats(self, client):
        client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_alias": "statstest"},
        )
        # Hit the redirect to increment click
        client.get("/statstest", follow_redirects=False)

        response = client.get("/stats/statstest")
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == "statstest"
        assert data["click_count"] == 1

    def test_stats_not_found(self, client):
        response = client.get("/stats/nope")
        assert response.status_code == 404


class TestQRCode:
    """GET /qr/{short_code}"""

    def test_qr_code(self, client):
        client.post(
            "/shorten",
            json={"url": "https://example.com", "custom_alias": "qrtest"},
        )
        response = client.get("/qr/qrtest")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        # Verify it's actually a PNG (magic bytes)
        assert response.content[:4] == b"\x89PNG"

    def test_qr_not_found(self, client):
        response = client.get("/qr/nope")
        assert response.status_code == 404


class TestHealth:
    """GET /health"""

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
