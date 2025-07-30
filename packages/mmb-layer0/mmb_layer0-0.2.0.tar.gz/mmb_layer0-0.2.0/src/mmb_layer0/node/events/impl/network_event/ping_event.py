from mmb_layer0.node.events.EventHandler import EventHandler
from mmb_layer0.node.node_event_handler import NodeEventHandler, NodeEvent
from mmb_layer0.p2p.peer import Peer
import time


class PingEvent(EventHandler):
    def __init__(self, node_event_handler: "NodeEventHandler"):
        super().__init__(node_event_handler)

    def require_field(self):
        return [] # Not required

    @staticmethod
    def event_name() -> str:
        return "ping"

    def handle(self, event: "NodeEvent"):
        self.neh.fire_to(event.origin, NodeEvent("pong", {}, self.neh.node.origin))

class PongEvent(EventHandler):
    def __init__(self, node_event_handler: "NodeEventHandler"):
        super().__init__(node_event_handler)
        self.peer_timer: dict[str, int] = {}

    @staticmethod
    def event_name() -> str:
        return "pong"

    def require_field(self):
        return [] # Not required

    def handle(self, event: "NodeEvent"):
        # check this peer is alive
        peer = self.neh.find_peer_by_address(event.origin)
        if peer is None:
            return False
        self.peer_timer[peer.address] = int(time.time())

        for p in self.neh.peers:
            if self.peer_timer[p.address] is None:
                continue
            if time.time() - self.peer_timer[p.address] > 10:
                self.safe_remove(p)

        return False

    def safe_remove(self, p: "Peer"):
        try:
            self.neh.peers.remove(p)
            self.peer_timer.pop(p.address)
        except Exception as e:
            print("[PongEvent] Safe remove Error!: " + str(e))
            pass