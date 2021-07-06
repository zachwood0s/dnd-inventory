from twisted.internet.protocol import Protocol, ClientFactory, ReconnectingClientFactory
from twisted.internet import reactor
from sys import stdout

import argparse

import time
import threading
import pickle

import ui
import packet
import resourceManager


class DNDClient(Protocol):
    def __init__(self):
        super().__init__()

        def worker(pkt):
            reactor.callFromThread(self.packet_listener, pkt)

        resourceManager.add_message_handler(worker)

    def connectionMade(self):
        print("connected")
        resourceManager.set_is_connected(True)

    def connectionLost(self, reason):
        print("lost connection")
        resourceManager.set_is_connected(False)

    def dataReceived(self, data):
        pkt: packet.Packet = pickle.loads(data)
        resourceManager.handle_incoming(pkt)

    def packet_listener(self, pkt: packet.Packet):
        if self.connected:

            print('sending packet', pkt.data)
            pickled = pickle.dumps(pkt)
            self.transport.write(pickled)
        else:
            pass


class DNDClientFactory(ReconnectingClientFactory):
    def __init__(self):
        super().__init__()

    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        resourceManager.set_is_connected(True)
        return DNDClient()

    def clientConnectionLost(self, connector, reason):
        resourceManager.set_is_connected(False)
        print('Lost connection.  Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('DND Inventory Manager')
    parser.add_argument('host')
    parser.add_argument('port', type=int)

    args = parser.parse_args()

    app = ui.App()

    def worker():
        app.run(fork=False)
        print('Exiting')
        reactor.callFromThread(reactor.stop)

    threading.Thread(target=worker).start()

    reactor.connectTCP(args.host, args.port, DNDClientFactory())
    reactor.run()
