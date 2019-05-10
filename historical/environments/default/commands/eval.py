syntax = r'^(?:\%|\+eval )(?P<statement>.+)$'

def eval(caller, statement):
    # We use caller.write directly to avoid unescaping the text.
    caller.write("< %s" % (eval(statement), ))

eval.safe = False
eval.complete = True
