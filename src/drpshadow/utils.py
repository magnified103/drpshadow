import os
from pathlib import Path


def get_drpshadow_root():
    return os.path.abspath(Path(__file__).parent.parent.parent)
