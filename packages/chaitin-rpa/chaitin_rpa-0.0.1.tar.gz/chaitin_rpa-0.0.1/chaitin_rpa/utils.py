import csv
import asyncio
from datetime import datetime

from chaitin_rpa.config import config, config_dir
from chaitin_rpa.database import db_path

sema = asyncio.BoundedSemaphore(config.MAX_CONNECTIONS)


def output_csv_dns(flagged_dns):
    time_str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    with open(f"flagged-dns-{time_str}.csv", "w+") as f:
        # merged = []
        # for dns_entry in flagged_dns:
        #    found = False
        #    for other_dns_entry in merged:
        #        if dns_entry["subdomain"] == other_dns_entry["subdomain"]:
        #            other_dns_entry["record"] += "," + dns_entry["record"]
        #            found = True
        #            break
        #    if not found:
        #        merged.append(dns_entry)

        # flagged_dns = merged

        # Write CSV Header, If you dont need that, remove this line
        writer = csv.writer(f)
        writer.writerow(
            [
                "id",
                "domain",
                "subdomain",
                "rdtype",
                "record",
                "status",
                "created_at",
            ]
        )

        for x in flagged_dns:
            writer.writerow(
                [
                    x["id"],
                    x["domain"],
                    x["subdomain"],
                    x["rdtype"],
                    x["record"],
                    x["status"],
                    x["created_at"],
                ]
            )


def output_csv_ip(flagged_ip):
    time_str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    with open(f"flagged-ip-{time_str}.csv", "w+") as f:
        # Write CSV Header, If you dont need that, remove this line
        writer = csv.writer(f)
        writer.writerow(
            [
                "id",
                "ip",
                "live_port",
                "whois",
                "status",
                "validated_ports",
                "flagged_ports",
                "new_ports",
            ]
        )

        for x in flagged_ip:
            writer.writerow(
                [
                    x["id"],
                    x["ip"],
                    x["live_port"],
                    x["as_name"],
                    x["status"],
                    " ".join([str(s) for s in x["validated_ports"]]),
                    " ".join([str(s) for s in x["flagged_ports"]]),
                    " ".join([str(s) for s in x["new_ports"]]),
                ]
            )


def backup_database(backup_dir=None):
    time_str = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    if not backup_dir:
        backup_dir = config_dir / "backups/"
    dest = backup_dir / f"{time_str}.db"

    backup_dir.mkdir(exist_ok=True)
    dest.write_bytes(db_path.read_bytes())
