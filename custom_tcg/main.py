"""Main functionality provided for all modules."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

logger: logging.Logger = logging.getLogger(name=__name__)


def setup() -> None:
    """Set up this file as main."""
    load_dotenv()

    log_dir: Path = Path.cwd().joinpath("logs")
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s %(levelname)s %(pathname)s"
            " %(lineno)s %(funcName)s %(message)s"
        ),
    )

    root_logger: logging.Logger = logging.getLogger()
    root_logger.setLevel(level=logging.DEBUG)

    file_handler = logging.FileHandler(
        filename=log_dir / "output.log",
        mode="w",
    )
    file_handler.setFormatter(fmt=formatter)
    root_logger.addHandler(hdlr=file_handler)

    console_handler: logging.StreamHandler = logging.StreamHandler(
        stream=sys.stdout,
    )
    console_handler.setFormatter(fmt=formatter)
    root_logger.addHandler(hdlr=console_handler)


def main() -> None:
    """Do the main function."""
    logger.info("Main executed successfully.")


if __name__ == "__main__":
    setup()
    main()
