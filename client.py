from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
from sys import stdout

import argparse


class DNDClient(Protocol):
    def dataReceived(self, data):
        data = data.decode()
        stdout.write(data)


class DNDClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        return DNDClient()

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('DND Inventory Manager')
    parser.add_argument('host')
    parser.add_argument('port', type=int)

    args = parser.parse_args()

    reactor.connectTCP(args.host, args.port, DNDClientFactory())
    reactor.run()
