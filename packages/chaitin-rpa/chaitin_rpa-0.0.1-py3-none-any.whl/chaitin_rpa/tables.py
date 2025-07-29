import asyncio
from sqlalchemy import DateTime, Table, Column, Integer, String
import chaitin_rpa.database

metadata = chaitin_rpa.database.metadata

IPTable = Table(
    "ip_table",
    metadata,
    Column("id", Integer, nullable=False, primary_key=True),
    Column("ip", String(32), nullable=False),
    Column("subnet", String(32)),
    Column("tags", String(256), nullable=False),
    Column("live_port", Integer, nullable=False),
    Column("as_name", String(256), nullable=False),
    Column("status", String(32), nullable=False),
    Column("first_flagged", DateTime),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
    Column("lastseen_at", DateTime, nullable=False),
)

PortTable = Table(
    "ip_ports_table",
    metadata,
    Column("id", Integer, nullable=False, primary_key=True),
    Column("ip", String(32), nullable=False),
    Column("port", Integer, nullable=False),
    Column("protocol", String(32), nullable=False),
    Column("service", String(32)),
    Column("tunnel", String(32)),
    Column("product", String(32)),
    Column("version", String(128)),
    Column("banner", String(128)),
    Column("categories", String(256), nullable=False),
    Column("status", String(32), nullable=False),
    Column("first_flagged", DateTime),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
    Column("lastseen_at", DateTime, nullable=False),
)

DNSTable = Table(
    "domain_table",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("domain", String(128), nullable=False),
    Column("subdomain", String(128), nullable=False),
    Column("rdtype", String(128), nullable=False),
    Column("record", String(128), nullable=False),
    Column("status", String(32), nullable=False),
    Column("first_flagged", DateTime),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
    Column("lastseen_at", DateTime, nullable=False),
)

PortsTable = Table("ports_table", metadata, Column("id", Integer, primary_key=True))


async def setup():
    async with chaitin_rpa.database.engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


asyncio.run(setup())
