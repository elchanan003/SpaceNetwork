from space_network_lib import SpaceNetwork, Packet
from satellite import Satellite
from relay_packet import RelayPacket
from sending_attempt import attempt_transmission, BrokenConnectionError
from earth import Earth

network = SpaceNetwork(4)

sat1 = Satellite("sat1", 100, network)
sat2 = Satellite("sat2", 200, network)
earth = Earth("Earth", 0)

p_final = Packet("Hello from Earth!!", sat1, sat2)
p_earth_to_sat1 = RelayPacket(p_final, earth, sat1)

try:
    attempt_transmission(network, p_earth_to_sat1)
except BrokenConnectionError:
    print("Transmission failed")

