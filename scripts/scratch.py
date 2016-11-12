from twisted.conch import recvline
from twisted.conch.insults import insults
from twisted.conch.telnet import TelnetTransport, TelnetBootstrapProtocol
from twisted.conch.manhole_ssh import ConchFactory, TerminalRealm

from twisted.internet import protocol
from twisted.application import internet, service
from twisted.cred import checkers, portal


clients = [] # We can probably search through the connections... but...

CTRL_C = '\x03'
CTRL_D = '\x04'
CTRL_BACKSLASH = '\x1c'
CTRL_L = '\x0c'


class DemoRecvLine(recvline.HistoricRecvLine):
    """Simple echo protocol.

    Accepts lines of input and writes them back to its connection.  If
    a line consisting solely of \"quit\" is received, the connection
    is dropped.
    """
    
    def handle_CTRLD(self):
        self.terminal.write("Received Control-D!")
        self.terminal.nextLine()
    
    def handle_CTRLC(self):
        self.terminal.write("Received Control-C!")
        self.terminal.nextLine()
    
    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)

        self.keyHandlers[CTRL_C] = self.handle_INT
        self.keyHandlers[CTRL_D] = self.handle_EOF
        self.keyHandlers[CTRL_L] = self.handle_FF
        self.keyHandlers[CTRL_BACKSLASH] = self.handle_QUIT
        
        for client in clients:
            client.terminal.nextLine()
            client.terminal.write("A new user has joined.")
            client.terminal.nextLine()
            client.drawInputLine()
        
        clients.append(self)
    
    
    #def connectionMade(self):
        #self.interpreter = ManholeInterpreter(self, self.namespace)

    def handle_INT(self):
        self.terminal.nextLine()
        self.terminal.write("KeyboardInterrupt")
        self.terminal.nextLine()
        self.terminal.write(self.ps[self.pn])
        self.lineBuffer = []
        self.lineBufferIndex = 0

    def handle_EOF(self):
        if self.lineBuffer:
            self.terminal.write('\a')
        else:
            self.handle_QUIT()

    def handle_FF(self):
        """
        Handle a 'form feed' byte - generally used to request a screen
        refresh/redraw.
        """
        self.terminal.eraseDisplay()
        self.terminal.cursorHome()
        self.drawInputLine()

    def handle_QUIT(self):
        self.terminal.loseConnection()
        
    def connectionLost(self, reason):
        if self in clients:
            clients.remove(self)
        
        for client in clients:
            client.terminal.nextLine()
            client.terminal.write("A new user has disconnected.")
            client.terminal.nextLine()
            client.drawInputLine()

        recvline.HistoricRecvLine.connectionLost(self, reason)
    
    def lineReceived(self, line):
        if line == "quit":
            self.terminal.loseConnection()
        
        self.terminal.write("You say, \"%s\"" % line)
        self.terminal.nextLine()
        self.drawInputLine()
        
        for client in clients:
            if client is self: continue
            client.terminal.nextLine()
            client.terminal.write("User says: %s" % line)
            client.terminal.nextLine()
            client.drawInputLine()


def makeService(factory, port, *args, **kw):
    f = protocol.ServerFactory()
    f.protocol = lambda: TelnetTransport(TelnetBootstrapProtocol, insults.ServerProtocol, factory, *args, **kw)
    tsvc = internet.TCPServer(port, f)
    
    return tsvc
    
    #m = service.MultiService()
    #tsvc.setServiceParent(m)
    #csvc.setServiceParent(m)
    #return m

application = service.Application("Insults RecvLine Demo")
makeService(DemoRecvLine, 6023).setServiceParent(application)

