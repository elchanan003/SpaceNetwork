import time
from space_network_lib import *

class BrokenConnectionError(Exception):
    pass

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
        except LinkTerminatedError:
            print("Link lost")
            raise BrokenConnectionError()
        except OutOfRangeError:
            print("Target out of range")
            raise BrokenConnectionError()