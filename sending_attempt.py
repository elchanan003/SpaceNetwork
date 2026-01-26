import time
from space_network_lib import *

def attempt_transmission(manager, packet):
    while True:
        try:
            manager.send(packet)
            return
        except TemporalInterferenceError:
            print("Interference, waiting...")
            time.sleep(2)
            continue
        except DataCorruptedError:
            print("Data corrupted, retrying...")
            continue