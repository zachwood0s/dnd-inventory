import lzma
import uuid

import hjson
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory, Protocol
from twisted.protocols import basic

from sanctum_dnd import packet
from sanctum_dnd.utils import ObjDecoder, Encoder


class DNDServer(basic.LineReceiver):
    MAX_LENGTH = 100000

    def __init__(self, users):
        self.users = users
        self.id = uuid.uuid4()

    def connectionMade(self):
        # self.factory was set by the factory's default buildProtocol:
        print('New user connected with id: ', self.id)

        if len(self.users) > 0:
            # Need to sync the data to the new user
            user = next(iter(self.users.values()))
            if user is not self:
                pkt = packet.make_sync_request_packet(None, '', 'server request')
                pickled = hjson.dumps(pkt, cls=Encoder).encode('utf-8')
                pickled = lzma.compress(pickled)
                user.sendLine(pickled)

        self.users[self.id] = self

    def connectionLost(self, reason):
        del self.users[self.id]
        print('User disconnected: ', self.id)

    def lineReceived(self, line):
        decomp = lzma.decompress(line)
        pkt = hjson.loads(decomp.decode('utf-8'), cls=ObjDecoder)
        print(f"Got packet from {pkt.sender}", str(pkt.data))

        for id_, user in self.users.items():
            if id_ != self.id:
                user.sendLine(line)


class DNDServerFactory(Factory):
    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr) -> "Protocol":
        return DNDServer(self.users)


if __name__ == '__main__':
    print('Starting server on port 1630')
    endpoint = TCP4ServerEndpoint(reactor, 1630)
    endpoint.listen(DNDServerFactory())
    reactor.run()
