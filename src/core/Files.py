import os
import ulid

BASE_STORAGE_DIR = "./files"


def get_new_uniq_file_path(prefix=""):
    name = str(ulid.api.new())

    if len(prefix) > 0:
        name = prefix + "_" + name

    return os.path.join(BASE_STORAGE_DIR, name)


def get_new_uniq_file(mode, prefix=""):
    """
    Open a new unique file
    :returns The handle to the new file
    """
    return open(get_new_uniq_file_path(prefix=prefix), mode=mode)
