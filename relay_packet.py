from space_network_lib import Packet

class RelayPacket(Packet):
    def __init__(self, packet_to_relay, sender, proxy):
        super().__init__(data = packet_to_relay, sender = sender, receiver = proxy)

    def __repr__(self):
        return f"RelayPacket (Relaying [{self.data}] to {self.receiver} from {self.sender})"
