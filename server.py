from client import DNDClientFactory
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor


class DNDServer(Protocol):
    def connectionMade(self):
        # self.factory was set by the factory's default buildProtocol:
        msg = self.factory.quote + '\r\n'
        self.transport.write(msg.encode())
        self.transport.loseConnection()


class DNDServerFactory(Factory):
    # This will be used by the default buildProtocol to create new protocols:
    protocol = DNDServer

    def __init__(self, quote=None):
        self.quote = quote or 'An apple a day keeps the doctor away'


endpoint = TCP4ServerEndpoint(reactor, 8007)
endpoint.listen(DNDServerFactory())
reactor.run()
