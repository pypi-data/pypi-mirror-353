import asyncio
from datetime import datetime
from typing import Any, Dict, List, TypedDict

from sqlalchemy.ext.asyncio import AsyncConnection
import curl_cffi
import xlsxwriter
from xlsxwriter.workbook import Worksheet

from chaitin_rpa.tables import DNSTable, IPTable, PortTable
from chaitin_rpa.utils import sema
from chaitin_rpa.config import config, config_dir


class IPResponse(TypedDict):
    id: int
    ip: str
    subnet: str
    version: int
    live_port: int
    as_name: str
    tags: List[str]
    status: str
    created_at: str
    updated_at: str
    lastseen_at: str


class PortResponse(TypedDict):
    id: int
    ip: str
    port: int
    protocol: str
    service: str
    tunnel: str
    product: str
    version: str
    banner: str
    categories: List[str]
    status: str
    created_at: str
    updated_at: str
    lastseen_at: str


class AssetInfo(IPResponse):
    validated_ports: List[PortResponse]
    flagged_ports: List[PortResponse]
    new_ports: List[PortResponse]


class DomainResponse(TypedDict):
    id: int
    domain: str
    subdomain: str
    rdtype: str
    record: str
    tags: List[str]
    status: str
    created_at: str
    updated_at: str
    lastseen_at: str


class HighRiskServiceResponse(TypedDict):
    id: str
    service: str
    protocol: str
    description: str
    port_count: int
    created_at: str
    updated_at: str
    lastseen_at: str


def parse_datetime(str: str) -> datetime:
    return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")


async def get_dns(params: Dict[str, Any] = {}) -> List[DomainResponse]:
    return await collate_all(
        "https://cmhk.asm.chaitin.cn/openapi/v1/asset/dns", params={**params, "flat": 1}
    )


async def get_ip(params: Dict[str, Any] = {}) -> List[IPResponse]:
    return await collate_all(
        "https://cmhk.asm.chaitin.cn/openapi/v1/asset/ip", params=params
    )


async def get_ports(params: Dict[str, Any] = {}) -> List[PortResponse]:
    return await collate_all(
        "https://cmhk.asm.chaitin.cn/openapi/v1/attack/port", params=params
    )


async def get_high_risk_services(
    params: Dict[str, Any] = {},
) -> List[HighRiskServiceResponse]:
    return await collate_all(
        "https://cmhk.asm.chaitin.cn/openapi/v1/risk/service", params=params
    )


async def collate_all(
    url: str,
    params: Dict[str, Any] = {},
    headers: Dict[str, str] = {},
    page_param="page",
):
    collated = []

    async with curl_cffi.AsyncSession() as s:
        s.headers.update(
            {
                "Content-Type": "application/json",
                "Token": config.CHAITIN_TOKEN,
                "Space": str(config.SPACE_ID),
            }
        )

        first_page = await s.get(url, params={**params}, headers=headers)
        data = first_page.json()["data"]

        if not data["items"] or len(data["items"]) == 0 or data["total"] == 0:
            return []
        pages = int(data["total"] / data["size"]) + (data["total"] % data["size"] > 0)
        tasks = []

        async def get_page(page):
            async with sema:
                return await s.get(
                    url, params={**params, page_param: page}, headers=headers
                )

        for i in range(1, pages):
            tasks.append(get_page(i))

        for task in asyncio.as_completed(tasks):
            current_response = await task
            data = current_response.json()["data"]
            items = data.get("items")
            collated.extend(items)

        return collated


### TODO: GATHER
async def collate_until(
    url: str,
    time_prop: str,
    after: datetime,
    before: datetime = datetime.now(),
    params={},
    headers={},
    page_param: str = "page",
):
    collated = []
    page = 1

    async with curl_cffi.AsyncSession() as s:
        s.headers.update(
            {
                "Content-Type": "application/json",
                "Token": config.CHAITIN_TOKEN,
                "Space": str(config.SPACE_ID),
            }
        )

        while True:
            async with sema:
                params.update({page_param: page})
                current_response = await s.get(url, params=params, headers=headers)
                data = current_response.json()["data"]
                items = data["items"]
                if len(items) == 0:
                    return []
                collated.extend(
                    [
                        x
                        for x in items
                        if parse_datetime(x[time_prop]) >= after
                        and parse_datetime(x[time_prop]) < before
                    ]
                )
                if parse_datetime(items[-1][time_prop]) < after or (
                    int(data["current"]) * int(data["size"])
                ) >= int(data["total"]):
                    break
                page += 1

        return collated


async def insert_domain(conn: AsyncConnection, domain: DomainResponse, flag: bool):
    processed = process_for_sqlite(domain)
    if flag:
        await conn.execute(
            DNSTable.insert(), {**processed, "first_flagged": datetime.now()}
        )
    else:
        await conn.execute(DNSTable.insert(), processed)


async def insert_ip(conn: AsyncConnection, ip: IPResponse, flag: bool):
    processed = process_for_sqlite(ip)
    if flag:
        await conn.execute(
            IPTable.insert(), {**processed, "first_flagged": datetime.now()}
        )
    else:
        await conn.execute(IPTable.insert(), processed)


async def insert_port(conn: AsyncConnection, port: PortResponse, flag: bool):
    processed = process_for_sqlite(port)
    if flag:
        await conn.execute(
            PortTable.insert(), {**processed, "first_flagged": datetime.now()}
        )
    else:
        await conn.execute(PortTable.insert(), processed)


def process_for_sqlite(item) -> Dict[str, Any]:
    #    processed = dict(item)
    #    if processed.get("tags") is not None:
    #        processed["tags"] = " ".join([str(s) for s in processed["tags"]])
    #    if processed.get("categories") is not None:
    #        processed["categories"] = " ".join([str(s) for s in processed["categories"]])
    #    processed["created_at"] = parse_datetime(processed["created_at"])
    #    processed["updated_at"] = parse_datetime(processed["updated_at"])
    #    processed["lastseen_at"] = parse_datetime(processed["lastseen_at"])
    #    return processed
    return {
        **item,
        "created_at": parse_datetime(item["created_at"]),
        "updated_at": parse_datetime(item["updated_at"]),
        "lastseen_at": parse_datetime(item["lastseen_at"]),
        "tags": (
            " ".join([str(s) for s in item["tags"]])
            if item.get("tags") is not None
            else None
        ),
        "categories": (
            " ".join([str(s) for s in item["categories"]])
            if item.get("categories") is not None
            else None
        ),
    }


def write_ip_worksheet(worksheet: Worksheet, ip_list: List[AssetInfo]):
    worksheet.write_row(
        0,
        0,
        [
            "id",
            "ip",
            "live_port",
            "whois",
            "status",
            "validated_ports",
            "flagged_ports",
            "new_ports",
            "created_at",
        ],
    )

    for i in range(len(ip_list)):
        x = ip_list[i]
        worksheet.write_row(
            i + 1,
            0,
            [
                x["id"],
                x["ip"],
                x["live_port"],
                x["as_name"],
                x["status"],
                ", ".join([str(s.get("port")) for s in x["validated_ports"]]),
                ", ".join([str(s.get("port")) for s in x["flagged_ports"]]),
                ", ".join([str(s.get("port")) for s in x["new_ports"]]),
                x["created_at"],
            ],
        )


def write_domain_worksheet(worksheet: Worksheet, domain_list: List[DomainResponse]):
    worksheet.write_row(
        0,
        0,
        [
            "id",
            "domain",
            "subdomain",
            "rdtype",
            "record",
            "status",
            "created_at",
        ],
    )

    for i in range(len(domain_list)):
        domain = domain_list[i]
        worksheet.write_row(
            i + 1,
            0,
            [
                domain["id"],
                domain["domain"],
                domain["subdomain"],
                domain["rdtype"],
                domain["record"],
                domain["status"],
                domain["created_at"],
            ],
        )


def generate_report(
    flagged_domains, new_domains, flagged_ips, new_ips, known_ips_with_open_ports
):
    # Create a workbook and add a worksheet.
    time_str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    workbook = xlsxwriter.Workbook(config_dir / f"{time_str}_chaitin_report.xlsx")
    write_domain_worksheet(workbook.add_worksheet("flagged_domains"), flagged_domains)
    write_domain_worksheet(workbook.add_worksheet("new_domains"), new_domains)

    write_ip_worksheet(workbook.add_worksheet("flagged_ips"), flagged_ips)
    write_ip_worksheet(workbook.add_worksheet("new_ips"), new_ips)
    write_ip_worksheet(
        workbook.add_worksheet("known_ips_with_open_ports"),
        known_ips_with_open_ports,
    )

    workbook.close()
