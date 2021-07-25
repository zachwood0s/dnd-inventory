import argparse
import lzma
import threading
from os import system

import hjson
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols import basic

from sanctum_dnd import resource_manager, packet, settings
from sanctum_dnd.ui.cli import main_form
from sanctum_dnd.utils import Encoder, ObjDecoder


class DNDClient(basic.LineReceiver):
    MAX_LENGTH = 100000

    def __init__(self):
        super().__init__()

        def worker(pkt):
            reactor.callFromThread(self.packet_listener, pkt)

        resource_manager.add_message_handler(worker)

    def connectionMade(self):
        print("connected")
        resource_manager.set_is_connected(True)

    def connectionLost(self, reason):
        print("lost connection. reason:", reason)
        resource_manager.set_is_connected(False)

    def lineReceived(self, line):
        line = lzma.decompress(line)
        pkt: packet.Packet = hjson.loads(line.decode('utf-8'), cls=ObjDecoder)
        resource_manager.handle_incoming(pkt)

    def packet_listener(self, pkt: packet.Packet):
        if self.connected:

            serial: bytes = hjson.dumps(pkt, cls=Encoder).encode('utf-8')
            serial = lzma.compress(serial)
            print(f'sending packet (size {len(serial)})', pkt.data)

            self.sendLine(serial)
        else:
            pass


class DNDClientFactory(ReconnectingClientFactory):
    def __init__(self):
        super().__init__()

    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        resource_manager.set_is_connected(True)
        return DNDClient()

    def clientConnectionLost(self, connector, reason):
        resource_manager.set_is_connected(False)
        print('Lost connection.  Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('DND Inventory Manager')
    parser.add_argument('host')
    parser.add_argument('port', type=int)

    args = parser.parse_args()

    system(f'mode con: cols={settings.MAX_WIDTH} lines={settings.MAX_HEIGHT}')

    app = main_form.App()


    def worker():
        app.run(fork=False)
        print('Exiting')
        reactor.callFromThread(reactor.stop)


    threading.Thread(target=worker).start()

    reactor.connectTCP(args.host, args.port, DNDClientFactory())
    reactor.run()
