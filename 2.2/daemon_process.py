#
# Communication Systems Lab
# Assignment 2
# Task 2.2
# ##############################
# Description:
# Parent class for creating a daemon process
# Under the guidance of "Advanced Programming in the UNIX Environment"
# and http://goo.gl/2k86Xd
#

import os, sys, time
# Cleaning job at exit
import atexit
# Signal for killing daemon
from signal import SIGTERM


class DaemonProcess(object):
    '''
    Parent class for creating daemon process. Deriving this class and calling
    start()to daemonize your process.

    Can only be used in root mode.
    '''

    def __init__(self, pid_file, stdin='/dev/null',
                 stdout='/dev/null', stderr='/dev/null'):
        '''
        Constructor, stdin, stdout and stderr will be redirected to
        /dev/null by default
        Specifying a PID file is mandantory.
        '''

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pid_file = pid_file

        # Permission check
        if os.geteuid():
            raise PermissionError('Permission denied, please run in root mode.')


    def daemonize(self):
        '''
        Daemonizing the server
        Under the guidance of APUE and goo.gl/2k86Xd
        '''

        # First fork and shutdown parent process
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #1 failed: %d (%s)\n' \
                             % (err.errno, err.strerror))
            sys.exit(1)

        # Decoupling from parent environment
        # Changing working directory to root
        os.chdir('/')
        # Creating new session
        os.setsid()
        # Setting umask to 0
        os.umask(0)

        #
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('fork #2 failed: %d (%s)\n' \
                             % (err.errno, err.strerror))
            sys.exit(1)

        # Redirecting standard IO desciptors
        sys.stdout.flush()
        sys.stderr.flush()
        null_in = open(self.stdin, 'r')
        null_out = open(self.stdout, 'a+')
        null_err = open(self.stderr, 'a+')
        os.dup2(null_in.fileno(), sys.stdin.fileno())
        os.dup2(null_out.fileno(), sys.stdout.fileno())
        os.dup2(null_err.fileno(), sys.stderr.fileno())

        # Writing PID file
        atexit.register(self.del_pidfile)
        pid = str(os.getpid())
        # Keeping occupying the PID file
        open(self.pid_file, 'w+').write('%s\n' % pid)


    def del_pidfile(self):
        '''
        Deleting the PID filei, registered by atexit
        '''

        os.remove(self.pid_file)


    def start(self):
        '''
        Starting the daemon process
        '''

        # Checking PID file existence.
        try:
            pid_file_fd = open(self.pid_file, 'r')
            pid = int(pid_file_fd.read().strip())
            pid_file_fd.close()
        except IOError:
            pid = None

        if pid:
            sys.stderr.write('Service is already running.\n')
            sys.exit(1)

        # Starting the daemon process
        self.daemonize()
        self.run()


    def stop(self):
        '''
        Stopping the daemon process
        '''

        # Fetching pid from the PID file
        try:
            pid_file_fd = open(self.pid_file, 'r')
            pid = int(pid_file_fd.read().strip())
            pid_file_fd.close()
        except IOError:
            pid = None

        if not pid:
            sys.stderr.write('Service is not running.\n')
            return 1

        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.5)
        except OSError as err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pid_file):
                    os.remove(self.pid_file)
            else:
                print(str(err))
                sys.exit(1)



    def restart(self):
        '''
        Restarting the daemon process
        '''

        self.stop()
        self.start()


    def run(self):
        '''
        Need to be overrided when derived, the daemon process actually
        works here.
        '''

