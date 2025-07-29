import logging
import configparser
from pathlib import Path

config_dir = Path.home() / "chaitin"

config_parser = configparser.ConfigParser({"ACCESS_TOKEN": ""}, allow_no_value=True)
config_parser.read(config_dir / "config.ini")


class Config:
    CHAITIN_TOKEN = config_parser.get("DEFAULT", "CHAITIN_TOKEN")
    SPACE_ID = config_parser.getint("DEFAULT", "SPACE_ID")
    APP_ID = config_parser.get("DEFAULT", "APP_ID")
    APP_SECRET = config_parser.get("DEFAULT", "APP_SECRET")
    TABLE_APP_TOKEN = config_parser.get("DEFAULT", "TABLE_APP_TOKEN")
    TABLE_PAGE_ID = config_parser.get("DEFAULT", "TABLE_PAGE_ID")
    RECEIVE_ID = config_parser.get("DEFAULT", "RECEIVE_ID")
    RECEIVE_ID_TYPE = config_parser.get("DEFAULT", "RECEIVE_ID_TYPE")
    DOMAIN_TEMPLATE_ID = config_parser.get("DEFAULT", "DOMAIN_TEMPLATE_ID")
    IP_TEMPLATE_ID = config_parser.get("DEFAULT", "IP_TEMPLATE_ID")
    ACCESS_TOKEN = (
        config_parser.get("DEFAULT", "ACCESS_TOKEN")
        if config_parser.get("DEFAULT", "ACCESS_TOKEN") != ""
        else None
    )
    MAX_CONNECTIONS = 5
    LOG_LEVEL = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }.get(config_parser.get("DEFAULT", "LOG_LEVEL"), logging.INFO)


config = Config()
