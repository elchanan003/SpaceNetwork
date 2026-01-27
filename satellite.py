from space_network_lib import SpaceEntity, Packet
from relay_packet import RelayPacket
from sending_attempt import attempt_transmission

class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth, network):
        super().__init__(name, distance_from_earth)
        self.network = network

    def receive_signal(self, packet: Packet):
        print(f"[{self.name}] Received: {packet}")

        if isinstance(packet, RelayPacket):
            inner_packet = packet.data
            print(f"Unwrapping and forwarding to {inner_packet.receiver}")
            attempt_transmission(self.network, inner_packet)
        else:
            print(f"Final destination reached: {packet.data}")



