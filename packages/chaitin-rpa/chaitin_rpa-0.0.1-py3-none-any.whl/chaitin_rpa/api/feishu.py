import asyncio
import json
import re
from urllib.parse import urljoin

import curl_cffi

from chaitin_rpa.config import config
from chaitin_rpa.log import logger


class BaseUrlSession(curl_cffi.AsyncSession):
    def __init__(self, base_url=""):
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self.base_url, url)
        return super().request(method, joined_url, *args, **kwargs)


async def get_tenant_access_token(app_id: str, app_secret: str):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": app_id, "app_secret": app_secret})
    headers = {"Content-Type": "application/json"}
    async with curl_cffi.AsyncSession() as s:
        response = await s.post(url, headers=headers, data=payload)
        tenant_access_token = response.json()["tenant_access_token"]
        logger.info(f"Successfully retrieved tenant_access_token：{tenant_access_token}")
        return tenant_access_token


def get_access_token():
    if config.ACCESS_TOKEN:
        return config.ACCESS_TOKEN
    else:
        return str(
            asyncio.run(get_tenant_access_token(config.APP_ID, config.APP_SECRET))
        )


access_token = get_access_token()


async def send_message(
    receive_id: str,
    content: dict[str, str],
    msg_type: str = "text",
    receive_id_type: str = "email",
):
    # 电子表格单元格的数据
    headers = {
        "content-type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    url = "https://open.feishu.cn/open-apis/im/v1/messages"

    body = {
        "receive_id": receive_id,
        "content": json.dumps(content),
        "msg_type": msg_type,
    }

    async with curl_cffi.AsyncSession(headers=headers) as s:
        response = await s.post(
            url, params={"receive_id_type": receive_id_type}, json=body, headers=headers
        )
        data = response.json()
        return data


async def read_table_base(app_token: str, table_id: str, view_id: str = ""):
    # 电子表格单元格的数据
    headers = {
        "content-type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    url = "https://open.feishu.cn/open-apis/bitable/v1/apps/{0}/tables/{1}/records/search".format(
        app_token, table_id
    )

    body = {
        "view_id": view_id,
        "automatic_fields": True,
    }

    async with curl_cffi.AsyncSession(headers=headers) as s:
        response = await s.post(
            url, params={"page_size": 500}, json=body, headers=headers
        )
        data = response.json()["data"]
        items = data.get("items")
        return items


def domain_filter(domain: str) -> bool:
    if re.match(r"hk\.chinamobile|\.hk|hk\.", domain):
        return True
    return True
