import os
import threading
import importlib
import argparse
import logging
import inspect
import time
import yaml
from rich_argparse import MetavarTypeRichHelpFormatter
import colorlog

from .worker import Worker
from . import __version__

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s[%(levelname)s] %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
)
logger = colorlog.getLogger("main")
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def load_extensions(extensions_dir: str, shared_config: dict, only: list[str] = None):
    if not os.path.isdir(extensions_dir):
        logger.error(f"The extensions directory '{extensions_dir}' does not exist.")
        return

    for root, _, files in os.walk(extensions_dir):
        for filename in files:
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            name_without_ext = os.path.splitext(filename)[0]
            if only and name_without_ext not in only:
                continue

            filepath = os.path.join(root, filename)
            relative_path = os.path.relpath(filepath, extensions_dir)
            module_name = os.path.splitext(relative_path)[0].replace(os.sep, ".")

            try:
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Worker) and obj is not Worker:
                        instance = obj(config=shared_config)
                        logger.info(f"Starting extension: {module_name}")
                        try:
                            threading.Thread(target=instance.run, daemon=True).start()
                        except Exception as e:
                            logger.error(
                                f"Extension '{module_name}' crashed during run: {e}"
                            )
                        break
                else:
                    logger.warning(f"No extension class found in {module_name}")

            except Exception as e:
                logger.error(f"Error loading extension {module_name} : {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Python Runner", formatter_class=MetavarTypeRichHelpFormatter
    )
    parser.add_argument(
        "-v", "--version", action="version", version=__version__, help="Show version"
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logs")
    parser.add_argument(
        "-e",
        "--extensions",
        type=str,
        default="extensions",
        help="Directory containing extensions",
    )
    parser.add_argument(
        "--only",
        type=str,
        default=None,
        help="Comma-separated list of extension names to load (e.g., foo,bar,baz)",
    )
    parser.add_argument(
        "-c", "--config", type=str, default=None, help="Path to configuration YAML file"
    )
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    if args.config:
        config_path = args.config
    else:
        if os.path.isfile("config.yaml"):
            config_path = "config.yaml"
        elif os.path.isfile("config.yml"):
            config_path = "config.yml"
        else:
            logger.error("No config file found (config.yaml or config.yml)")
            return

    only_list = args.only.split(",") if args.only else None

    logger.debug(f"Using config file: {config_path}")

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config file '{config_path}': {e}")
        return

    logger.info(f"Loading extensions from: {args.extensions}")
    load_extensions(args.extensions, config, only=only_list)
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info("Manual stop (Ctrl+C)")
