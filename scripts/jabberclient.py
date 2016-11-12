from twisted.protocols import jabber
from twisted.protocols.jabber import client,jid
from twisted.words.xish import domish
from twisted.internet import reactor


def presenceStanza(status=None, priority=None, show=None):
    pre = domish.Element(("jabber:client", "presence"))
    if status:
        pre.addElement("status", None, status)
    if priority:
        pre.addElement("priority", None, str(priority))
    if show:
        pre.addElement("show", None, show)
    return pre

def messageStanza(to, body, type='chat'):
    msg = domish.Element(("jabber:client", "message"))
    msg['type'] = type
    msg['to'] = to
    msg.addElement("body", None, body)
    return msg


def myMsgHandler(xmlstream):
    print "received message: %r" % str(xmlstream)
    message = messageStanza('alice@gothcandy.com', 'this is a tet')
    xmlstream.send(message)

def myPreHandler(xmlstream):
    print "received presence: %r" % str(xmlstream)

def myIqHandler(xmlstream):
    print "received iq: %r" % str(xmlstream)

def authd(xmlstream):
    print 'we\'ve authd!'

    presence = presenceStanza("available")
    xmlstream.send(presence)
    
    xmlstream.addObserver('/message',  myMsgHandler)
    xmlstream.addObserver('/presence', myPreHandler)
    xmlstream.addObserver('/iq',       myIqHandler)

def invaliduserEvent(xmlstream):
    print "failure to auth - invalid user"

def authfailedEvent(xmlstream):
    print "failure to authenticate"

myJid = jid.JID('portage@gothcandy.com/test')
factory = client.basicClientFactory(myJid,"PortageIsCool")

factory.addBootstrap('//event/stream/authd',authd)
factory.addBootstrap('//event/client/basicauth/invaliduser', invaliduserEvent)
factory.addBootstrap('//event/client/basicauth/authfailed',  authfailedEvent)


reactor.connectTCP('gothcandy.com',5222,factory)
reactor.run()
