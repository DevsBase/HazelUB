import ast
import importlib
import logging
import os
import runpy
import sys
import traceback
from pathlib import Path

from importlib.metadata import PackageNotFoundError, version
from typing import Dict, List, TypedDict, Any
from packaging.version import Version

from restart import restart
from .enums import USABLE, WORKS, PLATFORM

logger: logging.Logger = logging.getLogger(__name__)


class ModData(TypedDict):
    help: str
    works: WORKS
    usable: USABLE
    requires: Dict[str, str] | None
    platform: PLATFORM
    required_mods: List[str]


MODS_DATA: Dict[str, ModData] = {}


def config_checks(config: dict) -> bool:
    """
    Validate minimal config structure.
    """

    required: List[str] = ["name", "help", "works", "usable"]

    for key in required:
        if not config.get(key):
            return False

    return True


def resolve_ast(node: ast.AST) -> Any:
    """
    Convert AST nodes into real Python values.

    Supports:
    - literals
    - dict/list/tuple
    - enum references (WORKS.X, USABLE.X, PLATFORM.X)
    """

    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.Dict):
        return {
            resolve_ast(k): resolve_ast(v)
            for k, v in zip(node.keys, node.values)
        }

    if isinstance(node, ast.List):
        return [resolve_ast(el) for el in node.elts]

    if isinstance(node, ast.Tuple):
        return tuple(resolve_ast(el) for el in node.elts)

    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):

        enum_name: str = node.value.id
        attr: str = node.attr

        if enum_name == "WORKS":
            return getattr(WORKS, attr)

        if enum_name == "USABLE":
            return getattr(USABLE, attr)

        if enum_name == "PLATFORM":
            return getattr(PLATFORM, attr)

    raise ValueError("Unsupported AST node in MOD_CONFIG")


def extract_mod_config(file_path: str) -> dict | None:
    """
    Extract MOD_CONFIG from a module without executing it.
    """

    try:

        with open(file_path, "r", encoding="utf-8") as f:
            tree: ast.Module = ast.parse(f.read(), filename=file_path)

        for node in tree.body:

            if isinstance(node, ast.Assign):

                for target in node.targets:

                    if isinstance(target, ast.Name) and target.id == "MOD_CONFIG":

                        try:
                            return resolve_ast(node.value)

                        except Exception:

                            logger.warning(
                                f"[Mod Loader] MOD_CONFIG in {file_path} is unsupported."
                            )

                            return None

    except Exception:
        traceback.print_exc()

    return None


def install_package(pkg: str) -> None:
    """
    Install package using pip.
    """

    sys.argv = ["pip", "install", pkg]
    runpy.run_module("pip", run_name="__main__")


def get_installed_version(pkg: str) -> Version | None:
    """
    Return installed version of a package.
    """

    try:
        return Version(version(pkg))
    except PackageNotFoundError:
        return None


def check_requirement(pkg: str, constraint: str) -> bool:
    """
    Validate version constraint.
    """

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
    """
    Ensure required packages are installed.
    """

    restart_required: bool = False

    for pkg, constraint in reqs.items():

        installed: Version | None = get_installed_version(pkg)

        if installed is None:

            logger.warning(f"[Mod Loader] Installing missing package: {pkg}")

            install_package(pkg)

            restart_required = True
            continue

        if not check_requirement(pkg, constraint):

            logger.warning(
                f"[Mod Loader] Upgrading {pkg} (installed {installed}, requires {constraint})"
            )

            install_package(f"{pkg}{constraint}")

            restart_required = True

    if restart_required:
        restart()

    return True


def load_mods() -> None:
    """
    Load all mods safely."""

    global MODS_DATA

    mods_dir: Path = Path("Mods")
    mods_pkg: str = "Mods"

    loaded: List[str] = []

    for file in os.listdir(mods_dir):

        if not file.endswith(".py") or file.startswith("_"):
            continue

        file_path: Path = mods_dir / file
        module_name: str = file[:-3]
        module_path: str = f"{mods_pkg}.{module_name}"

        try:

            config: dict | None = extract_mod_config(str(file_path))

            if not config:
                continue

            if not config_checks(config):

                logger.warning(f"[Mod Loader] Invalid MOD_CONFIG in {file}")

                continue

            requires: Dict[str, str] | None = config.get("requires")
            required_mods: List[str] = config.get("required_mods", [])

            if requires and isinstance(requires, dict):
                ensure_requirements(requires)

            if required_mods and isinstance(required_mods, list):

                for req_mod in required_mods:

                    path: Path = mods_dir / req_mod

                    if not path.exists():

                        raise ModuleNotFoundError(
                            f"[Mod Loader] Required mod '{req_mod}' for '{config['name']}' not found."
                        )

            importlib.import_module(module_path)

            MODS_DATA[config["name"]] = {
                "help": config["help"],
                "works": config["works"],
                "usable": config["usable"],
                "requires": requires,
                "platform": config.get("platform") or PLATFORM.TELEGRAM,
                "required_mods": required_mods,
            }

            loaded.append(module_name)

        except Exception:

            traceback.print_exc()

            logger.error(f"[FAILED TO LOAD]: {module_path}. see error above ↑")

    logger.info(f"[Mods] Loaded: {', '.join(loaded)}")
