#!/usr/bin/python
 
import sys, os, time, atexit
from signal import SIGTERM
 
class Daemon(object):
    """
    A generic daemon class.
       
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, workdir="/" , stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.workdir = workdir
       
    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
       
        # decouple from parent environment
        os.chdir(self.workdir)
        os.setsid()
        os.umask(0)
       
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
       
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
       
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
    
    def appendChildPID(self, pid):
        file(self.pidfile,'a+').write("%s\n" % pid)
        
    def delpid(self):
        os.remove(self.pidfile)
 
    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
       
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
           
        # Start the daemon
        self.daemonize()
        self.run()
 
    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        pids = []
        try:
            pf = file(self.pidfile,'r')
            #pid = int(pf.read().strip())
            pidstr = pf.readlines()
            pids=[]
            for item in pidstr:
                item = item.strip()
                pids.append(item)
            pf.close()
        except IOError:
            pids = []
       
        if len(pids) == 0:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
        kill_pids = {}
        # Try killing the daemon process      
        for pid in pids:
            try:
                while 1:
                    os.kill(int(pid), SIGTERM)
                    time.sleep(0.1)
            except OSError, err:
                err = str(err)
                if err.find("No such process") > 0:
                    kill_pids[pid] = 1
                else:
                    print str(err)
                    sys.exit(1)
        if len(kill_pids) == len(pids):
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
            sys.stderr.write("all process are stoped")

        else:
            not_killed = " ".join(set(pids) - set(kill_pids))
            sys.stderr.write(not_killed)
            sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()
 
    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """