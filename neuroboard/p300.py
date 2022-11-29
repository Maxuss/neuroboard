from neuroplay.model.neuroplay import NeuroPlay
import numpy as np
import matplotlib.pyplot as plt
import time


def process():
    play = NeuroPlay()
    play.set_connected(True)
    play.enable_data_grab()
    play.start_record()

    time.sleep(1)

    sequence = np.array(play.grab_filtered_data()["data"][2])
    plt.acorr(sequence)
    plt.plot(sequence)
    plt.show()
