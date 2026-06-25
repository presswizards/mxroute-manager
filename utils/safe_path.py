import os


def path_under_base(base_dir, *parts):
    base = os.path.realpath(base_dir)
    joined = os.path.realpath(os.path.join(base, *parts))
    if joined != base and not joined.startswith(base + os.sep):
        raise ValueError("Invalid path")
    return joined


def safe_filename(name):
    name = os.path.basename(str(name or "").strip())
    if not name or name in (".", ".."):
        raise ValueError("Invalid filename")
    return name
