from space_network_lib import SpaceNetwork, Packet
from satellite import Satellite
from relay_packet import RelayPacket
from sending_attempt import attempt_transmission, BrokenConnectionError
from earth import Earth

network = SpaceNetwork(level=5)

earth = Earth("Earth", 0)

sat1 = Satellite("sat1", 100, network)
sat2 = Satellite("sat2", 200, network)
sat3 = Satellite("sat3", 300, network)
sat4 = Satellite("sat4", 400, network)


p_final = Packet("Hello from Earth!!", sat3, sat4)

p_sat2_to_sat3 = RelayPacket(p_final, sat2, sat3)
p_sat1_to_sat2 = RelayPacket(p_sat2_to_sat3, sat1, sat2)
p_earth_to_sat1 = RelayPacket(p_sat1_to_sat2, earth, sat1)

try:
    attempt_transmission(network, p_earth_to_sat1)
except BrokenConnectionError:
    print("Transmission failed")

