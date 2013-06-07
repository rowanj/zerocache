import zmq

class Server:
    def __init__(self):
        self.store = dict()
 
    def doFetch(self, socket, msgKey):
        #print ('doFetch %r' % (msgKey,))
        msgValue = self.store[msgKey]
        socket.send(msgKey, zmq.SNDMORE)
        socket.send(msgValue)
        
    def doStore(self, socket, msgKey, msgValue):
        #print ('doStore %r:%r' % (msgKey, msgValue))
        self.store[msgKey] = msgValue
        socket.send(msgKey)

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.REP)
        frontend.bind('tcp://*:5570')
 
        while True:
            msgKey = frontend.recv()
            if (not frontend.getsockopt(zmq.RCVMORE)):
                self.doFetch(frontend, msgKey)
            else:
                msgValue = frontend.recv()
                self.doStore(frontend, msgKey, msgValue)
 
        frontend.close()
        backend.close()
        context.term()
        
def main():
    """main function"""
    server = Server()
    server.run()
    
main()
        
print("done")
