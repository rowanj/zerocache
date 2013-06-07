import zmq
import easyzeroconf
import random

class Server:
    def __init__(self):
        self.store = dict()
        self.max_items = 1000000

    def shrink(self):
        self.store.pop(random.choice(self.store.keys))
 
    def doFetch(self, socket, msgKey):
        #print ('doFetch %r' % (msgKey,))
        if msgKey in self.store:
            msgValue = self.store[msgKey]
            socket.send(msgKey, zmq.SNDMORE)
            socket.send(msgValue)
        else:
            socket.send(msgKey)
        
    def doStore(self, socket, msgKey, msgValue):
        #print ('doStore %r:%r' % (msgKey, msgValue))
        self.store[msgKey] = msgValue
        socket.send(msgKey)
        while len(self.store) > self.max_items:
            self.shrink()

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.REP)
        port = frontend.bind_to_random_port('tcp://*', min_port=49152, max_port=65535, max_tries=200)
        print "bound to port %r" % (port,)
        easyzeroconf.register('ZeroCache', '_zerocache._tcp', port)
 
        try:
            while True:
                msgKey = frontend.recv()
                if (not frontend.getsockopt(zmq.RCVMORE)):
                    self.doFetch(frontend, msgKey)
                else:
                    msgValue = frontend.recv()
                    self.doStore(frontend, msgKey, msgValue)
        except KeyboardInterrupt:
            pass
 
        frontend.close()
        context.term()
        
def main():
    """main function"""
    server = Server()
    server.run()
    
main()
        
print("done")
