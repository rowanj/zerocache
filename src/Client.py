import zmq

class Client:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect('tcp://127.0.0.1:5570')
        
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

def main():
    client = Client()
    client.store('8', 'smeee')
    res = client.fetch('8')
    print "fetched: %r" % (res,)

main()
