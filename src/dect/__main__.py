import os
import logging

from dev.definitions import ROOT_DIR
from src.dect.postgresql_tasks import PostgresTasks
from src.dect.data import DectToPostgres
from src.dect.config import Configuration

#run module with 'python -m src.dect.__main__.py' in project root directory.
# instance of Configuration class
config = Configuration()

# instance of PostgresTasks class
client = PostgresTasks()

# initialize logging
loggingFile: str = os.path.join(ROOT_DIR, "dect210.log")

# config of logging module (DEBUG / INFO / WARNING / ERROR / CRITICAL)
logging.basicConfig(
    level=logging.INFO,
    filename=loggingFile,
    encoding="utf-8",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


dtop = DectToPostgres(config, client)
dtop.run()


# TODO: stop testing of ftop.run() after a certain time