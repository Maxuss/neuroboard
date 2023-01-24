import os
import threading
import shutil
from config import AppConfig
from datetime import datetime


def encode(record_index: int, bytes: bytes, training: str):
    """Encodes a record to file

    Args:
        record_index (int): Index of record to be encoded and saved
        bytes (bytes): Bytes result from calling the `capture` method
        training (str): Training data input, character sequence
    """
    threading.Thread(
        target=lambda: __encode_inner(record_index, bytes, training), daemon=True
    ).start()


def __encode_inner(record_index: int, bytes: bytes, training: str):
    if not os.path.exists("./nbdata"):
        os.makedirs("./nbdata")
    with open(f"nbdata/{datetime.date()}-{training}-{record_index}.ntd", "wb+") as file:
        file.write(f"{training}\0".encode("utf-8"))
        file.write(bytes)


def pack():
    """Packs the current neuroboard session training data to a tar.gz archive, and deletes previous training data"""
    if not os.path.exists("./nbdata"):
        return
    shutil.make_archive("./nb-training", "gztar", "./nbdata")
    shutil.rmtree("./nbdata")
