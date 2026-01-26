from space_network_lib import *
from satellite import Satellite

network = SpaceNetwork(1)
sat1 = Satellite("sat1", 100)
sat2 = Satellite("sat2", 200)

p1 = Packet("How you doing", sat1, sat2)
network.send(p1)