import pkgutil
import importlib
import Database.Tables

def load_models():
    for _, module_name, _ in pkgutil.iter_modules(Database.Tables.__path__):
        importlib.import_module(f"Database.Tables.{module_name}")
