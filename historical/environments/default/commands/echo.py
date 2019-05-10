syntax = r'^echo (?P<message>.+)$'

def echo(caller, message):
    commands.pemit(caller, caller, message)

echo.safe = True
echo.complete = True
