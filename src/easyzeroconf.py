import pybonjour
import threading
import select
import socket

class RegisterThread(threading.Thread):
    def __init__(self, name, regtype, port):
        threading.Thread.__init__(self)
        self.name = name
        self.regtype = regtype
        self.port = port
    
    def run(self):
        def register_callback(sdRef, flags, errorCode, name, regtype, domain):
            if errorCode == pybonjour.kDNSServiceErr_NoError:
                print 'Registered service:'
                print '  name    =', name
                print '  regtype =', regtype
                print '  domain  =', domain

        sdRef = pybonjour.DNSServiceRegister(name = self.name,
                                             regtype = self.regtype,
                                             port = self.port,
                                             callBack = register_callback)
        try:
            try:
                while True:
                    ready = select.select([sdRef], [], [])
                    if sdRef in ready[0]:
                        pybonjour.DNSServiceProcessResult(sdRef)
            except KeyboardInterrupt:
                pass
        finally:
            sdRef.close()

def register(name, regtype, port):
    registerThread = RegisterThread(name, regtype, port)
    registerThread.daemon = True
    registerThread.start()


class FindThread(threading.Thread):
    def __init__(self, regtype, callback):
        threading.Thread.__init__(self)
        self.regtype = regtype
        self.callback = callback
        self.resolved = []
        self.queried = []
        self.timeout = 10

    def run(self):
       def resolve_callback(sdRef, flags, interfaceIndex, errorCode, fullname,
                             hosttarget, port, txtRecord):
            if errorCode != pybonjour.kDNSServiceErr_NoError:
                return

            print 'Resolved service:'
            print '  fullname   =', fullname
            print '  hosttarget =', hosttarget
            print '  port       =', port

            def query_record_callback(sdRef, flags, interfaceIndex, errorCode, fullname,
                                      rrtype, rrclass, rdata, ttl):
                if errorCode == pybonjour.kDNSServiceErr_NoError:
                    ip = socket.inet_ntoa(rdata)
                    print '  IP         =', ip
                    self.queried.append(True)
                    self.callback(ip, port)

            query_sdRef = pybonjour.DNSServiceQueryRecord(interfaceIndex = interfaceIndex,
                                                          fullname = hosttarget,
                                                          rrtype = pybonjour.kDNSServiceType_A,
                                                          callBack = query_record_callback)

            try:
                while not self.queried:
                    ready = select.select([query_sdRef], [], [], self.timeout)
                    if query_sdRef not in ready[0]:
                        print 'Query record timed out'
                        break
                    pybonjour.DNSServiceProcessResult(query_sdRef)
                else:
                    self.queried.pop()
            finally:
                query_sdRef.close()

            self.resolved.append(True)
       

       def browse_callback(sdRef, flags, interfaceIndex, errorCode, serviceName,
                           regtype, replyDomain):
           if errorCode != pybonjour.kDNSServiceErr_NoError:
               return
            
           if not (flags & pybonjour.kDNSServiceFlagsAdd):
               print 'Service removed'
               return

           print 'Service added; resolving'

           resolve_sdRef = pybonjour.DNSServiceResolve(0,
                                                       interfaceIndex,
                                                       serviceName,
                                                       regtype,
                                                       replyDomain,
                                                       resolve_callback)

           try:
               while not self.resolved:
                   ready = select.select([resolve_sdRef], [], [], self.timeout)
                   if resolve_sdRef not in ready[0]:
                       print 'Resolve timed out'
                       break
                   pybonjour.DNSServiceProcessResult(resolve_sdRef)
               else:
                   self.resolved.pop()
           finally:
               resolve_sdRef.close()

       browse_sdRef = pybonjour.DNSServiceBrowse(regtype = self.regtype,
                                                 callBack = browse_callback)

       try:
           try:
               while True:
                   ready = select.select([browse_sdRef], [], [])
                   if browse_sdRef in ready[0]:
                       pybonjour.DNSServiceProcessResult(browse_sdRef)
           except KeyboardInterrupt:
               pass
       finally:
           browse_sdRef.close()

def find(regtype, callback):
    findThread = FindThread(regtype, callback)
    findThread.daemon = True
    findThread.start()
