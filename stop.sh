`ps xf | grep WebServer.py | grep -v 'grep' | awk '{print $1}' | xargs kill `
sleep 2

