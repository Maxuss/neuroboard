from neuroplay.model.neuroplay import NeuroPlay
import time
import os
import base64
import threading
import shutil


def capture(elements: int, max_passes: int, callback) -> bytes:
    """Captures data from the NeuroPlay device

    Args:
        elements (int): amount of elements (characters) that require parsing
        max_passes (int): Maximum amount of passes per character, depends on the total amount of characters
        callback (function): Function that will be called each time a pass proceeds

    Returns:
        bytes: Recorded bytes
    """

    play = NeuroPlay()
    play.set_connected(True)
    play.enable_data_grab()
    play.start_record()
    for element in range(0, elements):
        for j in range(0, 5):
            for i in range(0, max_passes):
                callback(i)
                # print(f"recording element {element} pass {i}")
                play.add_edf_annotation(f"element_{element}$char_{i}$pass_{j}")
                time.sleep(0.4)
    return base64.b64decode(play.stop_record()["files"][0]["data"])


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
    with open(f"nbdata/train-{record_index}.ntd", "wb+") as file:
        file.write(f"{training}\0".encode("utf-8"))
        file.write(bytes)


def pack():
    """Packs the current neuroboard session training data to a tar.gz archive, and deletes previous training data"""
    if not os.path.exists("./nbdata"):
        return
    shutil.make_archive("./nb-training", "gztar", "./nbdata")
    shutil.rmtree("./nbdata")
