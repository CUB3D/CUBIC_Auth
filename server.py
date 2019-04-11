import os

TEMPLATE_DIR = os.path.abspath("./templates")

from src.core import server


if __name__ == "__main__":
    server.start()
