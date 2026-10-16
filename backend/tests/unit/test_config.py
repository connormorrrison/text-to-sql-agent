import pytest

from app.config import Settings


def test_defaults_point_at_local_postgres(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.database_url.hosts()[0]["host"] == "localhost"
    assert settings.log_level == "INFO"


def test_env_vars_override_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@db.example:6543/demo")
    monkeypatch.setenv("AWS_REGION", "us-west-2")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.database_url.hosts()[0]["port"] == 6543
    assert settings.aws_region == "us-west-2"


def test_invalid_database_url_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "not-a-url")
    with pytest.raises(ValueError):
        Settings(_env_file=None)  # type: ignore[call-arg]
