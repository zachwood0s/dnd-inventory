from client import DNDClientFactory
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.protocols import basic
import time
import pickle
import uuid

import packet


class DNDServer(basic.LineReceiver):
    def __init__(self, users):
        self.users = users
        self.id = uuid.uuid4()

    def connectionMade(self):
        # self.factory was set by the factory's default buildProtocol:
        print('New user connected with id: ', self.id)

        if len(self.users) > 0:
            # Need to sync the data to the new user
            user = next(iter(self.users.values()))
            pkt = packet.make_sync_request_packet(None, '', 'server request')
            pickled = pickle.dumps(pkt)
            user.transport.write(pickled)

        self.users[self.id] = self

    def connectionLost(self, reason):
        del self.users[self.id]
        print('User disconnected: ', self.id)

    def lineReceived(self, line):
        pkt: packet.Packet = pickle.loads(line)
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
