from sqlalchemy.orm import DeclarativeBase
from test_project_fastapi.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
