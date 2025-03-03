from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models so that Alembic can detect them
from app.models import user, chat, message, material, session  # noqa
