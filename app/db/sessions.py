from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
