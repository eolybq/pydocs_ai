import json
import os

from loguru import logger

CHECKPOINT_FILE = "checkpoints.json"


def save_checkpoint(doc_name: str, last_index: int) -> None:
    data = {}
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            data = json.load(f)
    else:
        print(f"No checkpoint found for {doc_name}")
    data[doc_name] = {"last_index": last_index}
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f)


def load_checkpoint(doc_name: str) -> dict[str, int]:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            data = json.load(f)
        return data.get(doc_name, {"last_index": -1})
    logger.warning(f"No checkpoint found for {doc_name}")
    return {"last_index": -1}
