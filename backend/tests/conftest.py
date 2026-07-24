import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.workers import ai_models, queue_worker

TEST_DATABASE_URL = "postgresql+psycopg://smart_notes:smart_notes_dev_password@localhost:5432/smart_notes_test"
ADMIN_DATABASE_URL = "postgresql+psycopg://smart_notes:smart_notes_dev_password@localhost:5432/postgres"


def _ensure_test_database() -> None:
    admin_engine = create_engine(ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'smart_notes_test'")
        ).scalar()
        if not exists:
            conn.execute(text("CREATE DATABASE smart_notes_test"))
    admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def test_engine():
    _ensure_test_database()
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    session_factory = sessionmaker(bind=test_engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture()
def _mock_ai(monkeypatch):
    # Testes não devem carregar modelos de IA nem processar notas de verdade.
    monkeypatch.setattr(ai_models, "load_models", lambda: None)
    monkeypatch.setattr(queue_worker, "start_worker", lambda processor: None)
    monkeypatch.setattr(queue_worker, "enqueue", lambda note_id: None)


@pytest.fixture()
def client(db_session, _mock_ai):
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
