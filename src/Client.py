import zmq
import easyzeroconf
import time

class Client:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.LINGER, 10)
        
    def store(self, key, value):
        print ('sending store(%r:%r)' % (key,value))
        
        self.socket.send(key, zmq.SNDMORE)
        self.socket.send(value)
        
        #ignore result
        res = self.socket.recv()
        if self.socket.getsockopt(zmq.RCVMORE):
            res = self.socket.recv()

    def fetch(self, key):
        print ('sending fetch(%r)' % (key,))

        self.socket.send(key)
        
        self.socket.recv()
        res = dict()
        if self.socket.getsockopt(zmq.RCVMORE):
            res[key] = self.socket.recv()
        
        return res

    def connect(self, host, port):
        url = 'tcp://%s:%r' % (host, port)
        print 'connecting to %r' % (url,)
        self.socket.connect(url)

def find_servers(client):
    def callback(host, port):
        client.connect(host, port)

    easyzeroconf.find('_zerocache._tcp', callback)

def main():
    try:
        client = Client()
        find_servers(client)
        client.store('8', 'smeee')
        while True:
            for x in range(10):
                res = client.fetch('%r' % (x,))
                print "fetched: %r" % (res,)
                time.sleep(1)

    except KeyboardInterrupt:
        pass

main()
