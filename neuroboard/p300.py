from neuroplay.model.neuroplay import NeuroPlay
import time
import os
import base64
import threading
import shutil


def capture(record_index: int, passes: int) -> bytes:
    play = NeuroPlay()
    play.set_connected(True)
    play.enable_data_grab()
    play.start_record()
    for element in range(0, passes):
        for i in range(0, 5):
            print(f"recording element {element} pass {i}")
            play.add_edf_annotation(f"e_{element}$pass_{i}")
            time.sleep(0.5)
    return base64.b64decode(play.stop_record()["files"][0]["data"])


def encode(record_index: int, bytes: bytes, training: str):
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
    if not os.path.exists("./nbdata"):
        return
    shutil.make_archive("./nb-training", "gztar", "./nbdata")
