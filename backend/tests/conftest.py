import asyncio
import subprocess
from typing import AsyncGenerator

import asyncpg
import pytest
from database.db import Base, get_db
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import NullPool

from ..main import app


async def wait_for_postgres():
    print("Waiting for PostgreSQL")
    for i in range(60):
        print(f"check {i + 1}/60")

        try:
            conn = await asyncpg.connect(
                host="localhost",
                port=5433,
                user="testuser",
                password="testpass",
                database="testdb",
                timeout=2,
            )
            await conn.close()
            return True
        except:
            await asyncio.sleep(1)
    return False


subprocess.run(["docker", "rm", "-f", "test_postgres_17"], capture_output=True)
subprocess.run(
    [
        "docker",
        "run",
        "-d",
        "--name",
        "test_postgres_17",
        "-e",
        "POSTGRES_PASSWORD=testpass",
        "-e",
        "POSTGRES_USER=testuser",
        "-e",
        "POSTGRES_DB=testdb",
        "-p",
        "5433:5432",
        "postgres:17-alpine",
        "-c",
        "ssl=off",
        "-c",
        "max_connections=1024",
    ],
    check=True,
)

DATABASE_URL = (
    "postgresql+asyncpg://testuser:testpass@localhost:5433/testdb?ssl=disable"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = get_test_db


def pytest_addoption(parser):
    parser.addoption(
        "--ignore-highload", action="store_true", help="Ignore high load tests"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--ignore-highload"):
        skip_highload = pytest.mark.skip(reason=" тесты highload отключены")
        for item in items:
            if "highload" in item.keywords:
                item.add_marker(skip_highload)


@pytest.fixture(scope="session")
async def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    if not await wait_for_postgres():
        raise ConnectionError("PostgreSQL не доступен")
    else:
        print("PostgreSQL is running")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()
    subprocess.run(["docker", "stop", "test_postgres_17"], capture_output=True)
    subprocess.run(["docker", "rm", "test_postgres_17"], capture_output=True)


@pytest.fixture(scope="session")
async def client(setup_db) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), timeout=360, base_url="http://test"
    ) as client:
        yield client
