import os
import yaml
from configparser import ConfigParser
from dev.definitions import ROOT_DIR


class Configuration:
    def __init__(
        self,
        url_to_database: str = os.path.join(ROOT_DIR, "database.ini"),
        url_yaml_config: str = os.path.join(ROOT_DIR, "dect210_devices.yaml"),
    ):
        self.url_to_database = url_to_database
        self.url_yaml_config = url_yaml_config

    def dect210_config(self, section: str = "dect210") -> dict:
        """define the details of a connection to the fronius api based on database.ini"""
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(self.url_to_database)

        # get section
        dect_con = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                dect_con[param[0]] = param[1]
        else:
            raise Exception(
                f"Section {section} not found in the {self.url_to_database} file"
            )

        return dect_con

    def postgresql_config(self, section: str = "postgresql") -> dict:
        """define the details of a database connection based on database.ini"""
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(self.url_to_database)

        # get section
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception(
                f"Section {section} not found in the {self.url_to_database} file"
            )

        return db

    def yaml_config(self) -> dict:
        with open(self.url_yaml_config) as file:
            return yaml.load(file, Loader=yaml.FullLoader)
