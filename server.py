from client import DNDClientFactory
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
import time
import pickle
import uuid

import packet


class DNDServer(Protocol):
    def __init__(self, users):
        self.users = users
        self.id = uuid.uuid4()

    def connectionMade(self):
        # self.factory was set by the factory's default buildProtocol:
        print('New user connected with id: ', self.id)
        self.users[self.id] = self

    def connectionLost(self, reason):
        del self.users[self.id]
        print('User disconnected: ', self.id)

    def dataReceived(self, data: bytes):
        pkt: packet.Packet = pickle.loads(data)
        print(f"Got packet from {pkt.sender}", str(pkt.data))

        for id_, user in self.users.items():
            if id_ != self.id:
                user.transport.write(data)


class DNDServerFactory(Factory):
    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr) -> "Protocol":
        return DNDServer(self.users)


if __name__ == '__main__':
    print('Starting server on port 8007')
    endpoint = TCP4ServerEndpoint(reactor, 8007)
    endpoint.listen(DNDServerFactory())
    reactor.run()
