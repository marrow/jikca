syntax = r'^quit|disconnect|logoff|logout$'

def quit(caller):
    caller.transport.loseConnection()

quit.safe = True
quit.complete = True
