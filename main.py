from space_network_lib import *
from satellite import Satellite
from sending_attempt import *

network = SpaceNetwork(3)
sat1 = Satellite("sat1", 100)
sat2 = Satellite("sat2", 200)

p1 = Packet("Incoming meteor", sat1, sat2)

try:
    attempt_transmission(network, p1)
except BrokenConnectionError:
    print("Transmission failed")