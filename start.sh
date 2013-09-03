`ps xf | grep WebServer.py | grep -v 'grep' | awk '{print $2}' | xargs kill`
sleep 2
if [ $# -eq 1 ]; then
    if [ $1 = 'TEST' -o $1 = 'PROD' ]; then
        env=$1
    else
        echo "Error parameters, please input 'TEST' or 'PROD'"
        exit 1
    fi
    t=`ps xf|grep 'python WebServer.py' |grep -v 'grep' | wc -l`
    if [ $t -gt 0 ]; then
        echo "failed... service already exists."
    else
        export HEXINNELL=$env
        echo "export HEXINNELL="${HEXINNELL}
        echo "start service..."
        ulimit -c unlimited

        nohup python WebServer.py $1 > webserver.err 2>&1 &
        sleep 2
    fi
else
    echo "need one parms (TEST|PROD)"
fi

