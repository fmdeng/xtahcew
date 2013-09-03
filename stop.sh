`ps xf | grep WebServer.py | grep -v 'grep' | awk '{print $2}' | xargs kill`
sleep 2

