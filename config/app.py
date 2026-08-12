import os
from pathlib import Path

ENV_MODE = os.getenv("ENV_MODE", "local")
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "env" / f"{ENV_MODE}.env"
