import re

from .json import JSONStorage

__all__ = ["JSONStorage", "get_storage"]


def get_storage(storage_path: str):
    regex_str = r"(json)://([a-zA-Z0-9-_/]+)"
    matches = re.findall(regex_str, storage_path)

    if not matches:
        # No valid backend pattern found
        if "://" not in storage_path:
            raise ValueError(
                f"Invalid storage path '{storage_path}'. "
                "Storage paths must be in the format 'backend://path'. "
                "Currently supported: json://path"
            )
        else:
            # Extract the attempted backend for a better error message
            backend_part = storage_path.split("://")[0]
            raise ValueError(
                f"Unsupported storage backend '{backend_part}'. "
                "Currently supported backends: json. "
                f"Use 'json://path' instead of '{storage_path}'"
            )

    groups = matches[0]
    if len(groups) != 2:
        raise ValueError(
            "The storage backend must be specified in the form json://<file_path>"
        )

    backend = groups[0]
    path = groups[1]
    match backend:
        case "json":
            return JSONStorage(path)
        case _:
            raise ValueError(
                f"Unsupported storage backend '{backend}'. "
                "Currently supported backends: json. "
                f"Use 'json://path' instead of '{backend}://path'"
            )
