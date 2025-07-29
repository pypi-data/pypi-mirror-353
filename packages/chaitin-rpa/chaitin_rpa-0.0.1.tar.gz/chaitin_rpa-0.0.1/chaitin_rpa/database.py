import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

from chaitin_rpa.config import config_dir

db_path = config_dir / "latest.db"

engine = create_async_engine(
    f"sqlite+aiosqlite:///{db_path.absolute().as_posix()}",
    connect_args={"check_same_thread": False},
)
metadata = sa.MetaData()
