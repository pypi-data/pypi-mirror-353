from typing import List
import asyncio
import argparse
from pathlib import Path
import curl_cffi

from chaitin_rpa.config import config
from chaitin_rpa.api.feishu import read_table_base, send_message
from chaitin_rpa.api.cards import compose_domain_card, compose_ip_card, send_card
from chaitin_rpa.api.chaitin import (
    get_dns,
    get_ip,
    get_ports,
    insert_domain,
    insert_ip,
    insert_port,
    generate_report,
    DomainResponse,
    AssetInfo,
)
from chaitin_rpa.database import engine
from chaitin_rpa.tables import DNSTable, PortTable, IPTable
from chaitin_rpa.utils import (
    backup_database,
)
from chaitin_rpa.log import logger

parser = argparse.ArgumentParser(description="RPA automation for chaitin.")
subparsers = parser.add_subparsers(dest="subcommand")


def dir_path(string):
    if not string:
        return None
    path = Path(string)
    if path.is_dir():
        return path
    else:
        raise NotADirectoryError(string)


def subcommand(args=[], name="", parent=subparsers):
    def decorator(func):
        parser = parent.add_parser(
            func.__name__ if name == "" else name, description=func.__doc__
        )
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)

    return decorator


def argument(*name_or_flags, **kwargs):
    return ([*name_or_flags], kwargs)


async def _sync():
    try:
        ### TODO: Upload to cloud

        # content is json serialized str
        dns = await get_dns()
        ip_items = await get_ip()
        ports = await get_ports()

        ### Scrape table from feishu
        known_ips = []
        known_subdomains = []
        known_ports = {}

        known_hosts = await read_table_base(
            config.TABLE_APP_TOKEN, config.TABLE_PAGE_ID
        )

        for data_record in known_hosts:
            fields = data_record.get("fields")
            for substr in fields.get("\u57df\u540d", []):
                known_subdomains.append(substr.get("text"))
            for substr in fields.get("IP", []):
                splitted = substr.get("text").split(",")
                for subip in splitted:
                    known_ips.append(subip)

        ### Filter domains
        flagged_domains: List[DomainResponse] = []
        new_domains: List[DomainResponse] = []
        flagged_ips: List[AssetInfo] = []
        new_ips: List[AssetInfo] = []
        known_ips_with_open_ports: List[AssetInfo] = []
        async with engine.begin() as conn:

            """
            Step 1 Filter non-CMHK assets,
            Step 2 Find already flagged domains
            Step 3 Find newly added domains
            Step 4 Find already flagged IPs
            Step 5 Find already flagged ports & new ports
            Step 6 Find new IPs

            """

            for domain in dns:
                dns_exists = await conn.execute(
                    DNSTable.select().where(DNSTable.c.id == domain["id"])
                )
                if (
                    ### TODO: Tags
                    len(domain["tags"]) == 0
                    and domain["subdomain"] not in known_subdomains
                    ### Flag domain even if ip is in known_ips
                ):
                    if dns_exists.first():
                        flagged_domains.append(domain)
                    else:
                        new_domains.append(domain)
                        await insert_domain(conn, domain, True)
                else:
                    if not dns_exists.first():
                        await insert_domain(conn, domain, False)

            for ip in ip_items:
                ip_exists = await conn.execute(
                    IPTable.select().where(IPTable.c.id == ip.get("id"))
                )

                validated_ports = []
                flagged_ports = []
                new_ports = []

                selected_ports = list(filter(lambda x: x["ip"] == ip["ip"], ports))
                for port in selected_ports:
                    port_exists = await conn.execute(
                        PortTable.select().where(PortTable.c.id == port.get("id"))
                    )
                    if port["port"] not in known_ports.get(ip.get("ip"), []):
                        if port_exists.first():
                            flagged_ports.append(port)
                        else:
                            new_ports.append(port)
                            await insert_port(conn, port, True)
                    else:
                        if not port_exists.first():
                            await insert_port(conn, port, False)
                        validated_ports.append(port)

                merged: AssetInfo = {
                    **ip,
                    "validated_ports": validated_ports,
                    "flagged_ports": flagged_ports,
                    "new_ports": new_ports,
                }

                if (
                    ip.get("status") == "valid"
                    and len(ip.get("tags")) == 0
                    and (
                        ip.get("subnet")
                        not in [
                            "203.142.125.0/24",
                            "43.252.52.0/24",
                            "203.142.111.0/24",
                            "103.15.84.0/24",
                            "161.81.127.0/24",
                            "161.81.255.0/24",
                        ]
                    )
                    and ip.get("ip") not in known_ips
                ):
                    if ip_exists.first():
                        flagged_ips.append(merged)
                    else:
                        new_ips.append(merged)
                        await insert_ip(conn, ip, True)
                else:
                    if len(flagged_ports) == 0 and len(new_ports) == 0:
                        continue

                    known_ips_with_open_ports.append(merged)
                    if not ip_exists.first():
                        await insert_ip(conn, ip, False)

        generate_report(
            flagged_domains,
            new_domains,
            flagged_ips,
            new_ips,
            known_ips_with_open_ports,
        )

        await send_card(
            compose_domain_card, flagged_domains, "Flagged domains detected", "red"
        )
        await send_card(
            compose_domain_card, new_domains, "New domains detected", "yellow"
        )

        await send_card(compose_ip_card, flagged_ips, "Flagged IPs detected", "red")
        await send_card(compose_ip_card, new_ips, "New IPs detected", "yellow")
        await send_card(
            compose_ip_card,
            known_ips_with_open_ports,
            "Known IPs with open ports detected",
            "orange",
        )

        backup_database()

    except curl_cffi.exceptions.JSONDecodeError:
        return logger.info("Invalid json received")


async def _test_cmd():
    async with engine.begin() as conn:
        ip = await conn.execute(IPTable.select())
        await send_message(config.TARGET_EMAIL, compose_ip_card(ip.first()), msg_type="interactive")  # type: ignore


#    import json
#
#    ip_port_items = await collate_all("https://cmhk.asm.chaitin.cn/openapi/v1/attack/port")
#    with open("openport.json", "w+") as f:
#        json.dump(ip_port_items, f, indent=2)
#


@subcommand([])
def sync(_):
    asyncio.run(_sync())


@subcommand([])
def test_cmd(_):
    asyncio.run(_test_cmd())


@subcommand(
    [
        argument(
            "--dir", type=dir_path, default=None, help="specify a directory to write to"
        ),
    ]
)
def backup(args):
    backup_database(args.dir)


def run():
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)
