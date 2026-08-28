from django.test import Client


def test_live_health_check_does_not_require_dependencies() -> None:
    response = Client().get("/api/v1/health/live/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
