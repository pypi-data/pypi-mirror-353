from typing import Sequence, TypeVar, Protocol, Sized

from chaitin_rpa.config import config
from chaitin_rpa.api.chaitin import AssetInfo, DomainResponse
from chaitin_rpa.api.feishu import send_message


def compose_domain_card(
    data: Sequence[DomainResponse], card_title: str, banner_color: str
) -> dict:
    return {
        "type": "template",
        "data": {
            "template_id": config.DOMAIN_TEMPLATE_ID,
            "template_variable": {
                "card_title": card_title,
                "banner_color": banner_color,
                "object_list": [
                    {
                        "domain": d["domain"],
                        "subdomain": d["subdomain"],
                        "record": d["record"],
                    }
                    for d in data[:50]  # Message may be too long
                ],
                "card_footer": f"*{min(len(data), 50)}/{len(data)} total*",
            },
        },
    }


def compose_ip_card(
    data: Sequence[AssetInfo], card_title: str, banner_color: str
) -> dict:
    return {
        "type": "template",
        "data": {
            "template_id": config.IP_TEMPLATE_ID,
            "template_variable": {
                "card_title": card_title,
                "banner_color": banner_color,
                "object_list": [
                    {
                        "ip": ip["ip"],
                        "as_name": ip["as_name"],
                        "validated_ports": ", ".join(
                            [str(s.get("port")) for s in ip["validated_ports"]]
                        ),
                        "flagged_ports": ", ".join(
                            [str(s.get("port")) for s in ip["flagged_ports"]]
                        ),
                        "new_ports": ", ".join(
                            [str(s.get("port")) for s in ip["new_ports"]]
                        ),
                    }
                    for ip in data[:50]  # Message may be too long
                ],
                "card_footer": f"*{min(len(data), 50)}/{len(data)} total*",
            },
        },
    }
    # return {
    #    "config": {"wide_screen_mode": True},
    #    "elements": [
    #        {
    #            "tag": "div",
    #            "text": {
    #                "content": "IP 1.1.1.1",
    #                "tag": "lark_md",
    #            },
    #        },
    #        {
    #            "tag": "column_set",
    #            "flex_mode": "none",
    #            "background_style": "default",
    #            "columns": [
    #                {
    #                    "tag": "column",
    #                    "width": "weighted",
    #                    "weight": 1,
    #                    "vertical_align": "top",
    #                    "elements": [
    #                        {
    #                            "tag": "markdown",
    #                            "content": "${person}",
    #                            "text_align": "center",
    #                        }
    #                    ],
    #                },
    #                {
    #                    "tag": "column",
    #                    "width": "weighted",
    #                    "weight": 1,
    #                    "vertical_align": "top",
    #                    "elements": [
    #                        {
    #                            "tag": "markdown",
    #                            "content": "${time}",
    #                            "text_align": "center",
    #                        }
    #                    ],
    #                },
    #                {
    #                    "tag": "column",
    #                    "width": "weighted",
    #                    "weight": 1,
    #                    "vertical_align": "top",
    #                    "elements": [
    #                        {
    #                            "tag": "markdown",
    #                            "content": "${week_rate}",
    #                            "text_align": "center",
    #                        }
    #                    ],
    #                },
    #            ],
    #            "_varloop": "${group_table}",
    #        },
    #    ],
    #    "header": {
    #        "template": "red",
    #        "title": {
    #            "content": "New unknown IP exposed to public internet",
    #            "tag": "plain_text",
    #        },
    #    },
    # }


T = TypeVar("T", bound=Sized, contravariant=True)


class CardComposer(Protocol[T]):
    def __call__(self, data: T, card_title: str, banner_color: str) -> dict:
        ...


async def send_card(card_composer: CardComposer[T], data: T, *args):
    if len(data) > 0:
        await send_message(
            config.RECEIVE_ID,
            card_composer(data, *args),
            msg_type="interactive",
            receive_id_type=config.RECEIVE_ID_TYPE,
        )
