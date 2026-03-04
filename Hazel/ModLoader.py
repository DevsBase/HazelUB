import importlib
import logging
import os
import traceback
import runpy
import sys

from importlib.metadata import PackageNotFoundError, version
from typing import Dict, List, TypedDict
from packaging.version import Version

from restart import restart
from .enums import USABLE, WORKS

logger = logging.getLogger(__name__)

class ModHelp(TypedDict):
    help: str
    works: WORKS
    usable: USABLE


MODS_HELP: Dict[str, ModHelp] = {}


def config_checks(config: dict) -> bool:
    required: List[str] = ["name", "help", "works", "usable"]

    for key in required:
        if not config.get(key):
            return False
    return True


def install_package(pkg: str) -> None:
    sys.argv = ["pip", "install", pkg]
    runpy.run_module("pip", run_name="__main__")


def get_installed_version(pkg: str) -> Version | None:
    try:
        return Version(version(pkg))
    except PackageNotFoundError:
        return None


def check_requirement(pkg: str, constraint: str) -> bool:
    installed: Version | None = get_installed_version(pkg)

    if installed is None:
        return False

    required: Version = Version(constraint[2:])

    if constraint.startswith(">="):
        return installed >= required
    if constraint.startswith("<="):
        return installed <= required
    if constraint.startswith("=="):
        return installed == required
    if constraint.startswith(">"):
        return installed > required
    if constraint.startswith("<"):
        return installed < required

    return True


def ensure_requirements(reqs: Dict[str, str]) -> bool:
    restart_required: bool = False

    for pkg, constraint in reqs.items():

        installed: Version | None = get_installed_version(pkg)

        if installed is None:
            logger.warning(f"[MOD DEP] Installing missing package: {pkg}")
            install_package(pkg)
            restart_required = True
            continue

        if not check_requirement(pkg, constraint):
            logger.warning(
                f"[MOD DEP] Upgrading {pkg} (installed {installed}, requires {constraint})"
            )
            install_package(f"{pkg}{constraint}")
            restart_required = True

    if restart_required:
        logger.info("[MOD DEP] Restart required after dependency install.")
        restart()

    return True


def load_mods() -> None:
    global MODS_HELP

    mods_dir: str = os.path.join(os.path.dirname(__file__), "Mods")
    mods_pkg: str = f"{__package__}.Mods"

    loaded: List[str] = []

    for file in os.listdir(mods_dir):
        if not file.endswith(".py") or file.startswith("_"):
            continue

        module_name: str = file[:-3]
        module_path: str = f"{mods_pkg}.{module_name}"

        try:
            module = importlib.import_module(module_path)

            if hasattr(module, "MOD_CONFIG"):

                config: dict = getattr(module, "MOD_CONFIG")

                if not isinstance(config, dict) or not config_checks(config):
                    continue

                requires: Dict[str, str] | None = config.get("requires")

                if requires and isinstance(requires, dict):
                    ensure_requirements(requires)

                MODS_HELP[config["name"]] = {
                    "help": config["help"],
                    "works": config["works"],
                    "usable": config["usable"],
                }

            loaded.append(module_name)

        except Exception:
            traceback.print_exc()
            logger.error(f"[FAILED TO LOAD]: {module_path}. see error above ↑")

    logger.info(f"[Mods] Loaded: {', '.join(loaded)}")