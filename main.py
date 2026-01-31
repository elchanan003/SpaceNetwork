import time
from space_network_lib import *
from hashlib import sha256

network = SpaceNetwork(level=6)
MAX_DIST = 150

# שגיאות מותאמות אישית
class BrokenConnectionError(Exception):
    pass

class SecurityBreachError(Exception):
    pass

# הצפנת xor
def xor_cipher(text, key):
    result = []
    for i in range(len(text)):
        char = ord(text[i])
        ch_key = ord(key[i % len(key)])
        ch_pin = chr(char ^ ch_key)
        result.append(ch_pin)
    result = "".join(result)
    return result

#האש
def get_hash(key):
    return sha256(str(key).encode()).hexdigest()

# חבילה עם data מוצפן
class EncryptedPacket(Packet):
    def __init__(self, data, sender, receiver, key):
        super().__init__(data, sender, receiver)
        self.key = get_hash(key)
        self.data = xor_cipher(data, key)

    def decrypt(self, key):
        if get_hash(key) == self.key:
            return xor_cipher(self.data, key)
        else:
            raise SecurityBreachError

# לווין
class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth, key):
        super().__init__(name, distance_from_earth)
        self.key = key

    def receive_signal(self, packet: Packet):
        print(f"[{self.name}] Received: {packet}")

        if isinstance(packet, RelayPacket):
            inner_packet = packet.data
            print(f"Unwrapping and forwarding to {inner_packet.receiver}")
            attempt_transmission(network, inner_packet)
        else:
            if isinstance(packet, EncryptedPacket):
                try:
                    message = packet.decrypt(self.key)
                    print(f"Final destination reached: {message}")
                except SecurityBreachError:
                    print("מישהו ניסה לעבוד עליי עם מפתח לא נכון!")
            else:
                print(f"Final destination reached: {packet.data}")

# כדור הארץ
class Earth(SpaceEntity):
    def __init__(self, name, distance_from_earth, key):
        super().__init__(name, distance_from_earth)
        self.key = key

    def receive_signal(self, packet: Packet):
        print(f"[{self.name}] Received: {packet}")

        if isinstance(packet, RelayPacket):
            inner_packet = packet.data
            print(f"Unwrapping and forwarding to {inner_packet.receiver}")
            attempt_transmission(network, inner_packet)
        else:
            if isinstance(packet, EncryptedPacket):
                try:
                    message = packet.decrypt(self.key)
                    print(f"Final destination reached: {message}")
                except SecurityBreachError:
                    print("מישהו ניסה לעבוד עליי עם מפתח לא נכון!")
            else:
                print(f"Final destination reached: {packet.data}")

# חבילות ממסר
class RelayPacket(Packet):
    def __init__(self, packet_to_relay, sender, proxy):
        super().__init__(data = packet_to_relay, sender = sender, receiver = proxy)

    def __repr__(self):
        return f"RelayPacket (Relaying [{self.data}] to {self.receiver} from {self.sender})"

# שליחה כולל טיפול בשגיאות
def attempt_transmission(manager: SpaceNetwork, packet):
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


# מציאת נתיב קצר לשליחת הפאקטה בין גופים רחוקים
def smart_send_packet(satellites: list, packet:Packet):

    # חישוב מרחק בין המקור ליעד
    sender_dist = packet.sender.distance_from_earth
    receiver_dist = packet.receiver.distance_from_earth
    distance = abs(sender_dist - receiver_dist)

    #אם הטווח המקורי תקין - שולחים את ההודעה מיד
    if distance <= MAX_DIST:
        return attempt_transmission(network, packet)

    else:
        current_receiver = packet.sender
        route_satellites = []

        while True:
            # בכל איטרציה הלווין הקולט הופך למקור החדש
            current_sender = current_receiver
            #המרחק בין הלווין הנוכחי ליעד הסופי
            current_dist_to_final = abs(current_sender.distance_from_earth - packet.receiver.distance_from_earth)

            if current_dist_to_final <= MAX_DIST:
                break

            distance = 0
            for sat in satellites:

                # המרחק בין השולח ללווין הנוכחי
                dist_to_sat = abs(sat.distance_from_earth - current_sender.distance_from_earth)
                #המרחק בין הלווין הנוכחי החדש ליעד הסופי
                dist_to_final = abs(sat.distance_from_earth - packet.receiver.distance_from_earth)

                #סינון של פרוקסי רלונטי
                if dist_to_sat == 0:
                    continue
                if dist_to_sat > MAX_DIST:
                    continue
                if dist_to_final >= current_dist_to_final:
                    continue

                # בחירה בפרוקסי הכי רחוק שבטווח
                if dist_to_sat > distance:
                    current_receiver = sat
                    distance = dist_to_sat

            if current_sender == current_receiver:
                break

            # הוספת הלווינים שנבחרו לרשימה סופית
            route_satellites.append(current_receiver)


        # יצירת הודעת ממסר בין הגופים שברשימה הסופית
        #הודעה פנימית
        packet.sender = route_satellites.pop()
        final_pac = packet


        #טיפול במקרה של פרוקסי בודד
        if len(route_satellites) == 0:
            relay_pac = RelayPacket(final_pac, packet.sender, final_pac.sender)
            return attempt_transmission(network, relay_pac)

        #הודעת ממסר לפרוקסי נוסף
        relay_pac = RelayPacket(final_pac, route_satellites.pop(), final_pac.sender)

        #הוספת קימפולים לפי מספר הגופים שיש ברשימה
        while len(route_satellites) > 0:
            relay_pac = RelayPacket(relay_pac, route_satellites.pop(), relay_pac.sender)

        #הוספת שליחה מהשולח המקורי לפרוקסי הראשון
        final_packet = RelayPacket(relay_pac, packet.sender, relay_pac.sender)
        return attempt_transmission(network ,final_packet)



if __name__ == "__main__":

    earth = Earth("Earth", 0, "key")

    sat1 = Satellite("sat1", 100, "key")
    sat2 = Satellite("sat2", 200, "key")
    sat3 = Satellite("sat3", 300, "key")
    sat4 = Satellite("sat4", 400, "key")

    satellites_ = [sat1, sat2, sat3, sat4]
    packet_ = EncryptedPacket("חייזרים בדרך אליכם, הכניסו בירות למקפיא", sat3, earth, "key")

    try:
        smart_send_packet(satellites_, packet_)
    except BrokenConnectionError:
        print("Transmission failed")

