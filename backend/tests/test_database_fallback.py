from app.core import database as database_module


def test_postgres_url_falls_back_to_sqlite(monkeypatch):
    created_urls = []

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, *_args, **_kwargs):
            raise RuntimeError("postgres unavailable")

    class FakeEngine:
        def connect(self):
            return FakeConnection()

    def fake_create_engine(url, **kwargs):
        created_urls.append(url)
        if url.startswith("postgres"):
            return FakeEngine()
        return {"url": url}

    monkeypatch.setattr(database_module, "create_engine", fake_create_engine)

    engine = database_module._create_engine("postgresql://user:pass@localhost:5432/test")

    assert engine == {"url": "sqlite:///./pulse_ai.db"}
    assert created_urls == [
        "postgresql://user:pass@localhost:5432/test",
        "sqlite:///./pulse_ai.db",
    ]
