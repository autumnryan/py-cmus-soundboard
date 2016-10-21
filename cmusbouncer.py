import time
import socket
import subprocess
from pycmus import remote

class CmusBouncer(remote.PyCmus):
    def __init__(self, start_cmd=None, server=None, socket_path=None,
                 password=None, port=3000, keymap={}):
        try:
            super(CmusBouncer, self).__init__(server=server,
                                              socket_path=socket_path,
                                              password=password, port=port)

        except socket.error as err:
            if start_cmd:
                print 'Starting cmus...'
                subprocess.call(start_cmd.split(' '))
                time.sleep(1)
                super(CmusBouncer, self).__init__(server=server,
                                                  socket_path=socket_path,
                                                  password=password, port=port)
            else:
                print 'Could not connect to cmus: {0}'.format(str(err))

        self.keymap = keymap

        # Setup some known state: stopped, loop file
        self.player_stop()
        self.send_cmd('set repeat_current=1\n')

    def handle_key(self, key):
        cmus_action, args = self.keymap.get(key, (None, None))
        if cmus_action:
            if args:
                cmus_action(self, args)
            else:
                cmus_action(self)
