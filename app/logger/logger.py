import sys
from datetime import datetime
from loguru import logger as lologger

PrintLevel = "INFO"


def defineLogLevel(printLevel="INFO", logfileLevel="DEBUG", name: str = None):
    """Adjust the log level to above level"""
    global PrintLevel
    PrintLevel = printLevel

    currentDate = datetime.now()
    formattedDate = currentDate.strftime("%Y%m%d%H%M%S")
    logName = (
        f"{name}_{formattedDate}" if name else formattedDate
    )  # name a log with prefix name

    lologger.remove()
    lologger.add(sys.stderr, level=PrintLevel)
    return lologger


logger = defineLogLevel()