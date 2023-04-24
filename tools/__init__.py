import os

from core import config

if not os.path.exists(config.base_path):
    os.mkdir(config.base_path)
