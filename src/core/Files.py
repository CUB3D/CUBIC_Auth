import os
import random

BASE_STORAGE_DIR = "./files"


def gen_filename(length=32):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    return "".join([random.choice(alphabet) for _ in range(length)])


def get_new_uniq_file_path(prefix=""):
    name = gen_filename()

    if len(prefix) > 0:
        name = prefix + "_" + name

    return os.path.join(BASE_STORAGE_DIR, name)


def get_new_uniq_file(mode, prefix=""):
    """
    Open a new unique file
    :returns The handle to the new file
    """
    return open(get_new_uniq_file_path(prefix=prefix), mode=mode)
