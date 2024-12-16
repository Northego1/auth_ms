import subprocess
import sys
import os
import pytest



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# @pytest.fixture(scope="session", autouse=True)
# def apply_test_migrations():
#     subprocess.run(
#         "alembic", "-x", f"db_url={settings.db.test_postgres_dsn}", "upgrade", "head"
#     )


# @pytest.fixture(scope="session", autouse=True)
# def replace_uow():
#     providers.Factory(
#         UnitOfWorkImpl,
#         session=providers.Callable(lambda: provide_test_session().__aenter__())
#     )