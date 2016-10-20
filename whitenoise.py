#!/usr/bin/env python
import os, sys
import time
import curses # for easy input
import socket # for pycmus errors
import subprocess # to kick off cmus
from pycmus import remote
from optparse import OptionParser, OptionGroup

# TODO: CONFIG FILE
DEFAULT_CMUS_CMD = "screen -dmS cmus cmus".split(' ')
SONG_KEYMAP = {
    '1' : 'soft.mp3',
    '2' : 'pinknoise.mp3',
    '3' : 'whitenoise.mp3',
    '4' : 'ocean.mp3',
    '5' : 'rain.mp3',
    '6' : 'waves.mp3',
    '7' : 'nostromo.mp3',
    '8' : 'shoshonesunset.mp3',
    '9' : 'glowingsea.mp3',
    '0' : 'narshadda.mp3',
    }

class CmusRemote(remote.PyCmus):
    def __init__(self, start_cmd=None, server=None, socket_path=None,
                 password=None, port=3000, keymap={}):
        try:
            super(CmusRemote, self).__init__(server=server,
                                             socket_path=socket_path,
                                             password=password, port=port)

        except socket.error as err:
            if start_cmd:
                print 'Starting cmus...'
                subprocess.call(start_cmd)
                time.sleep(1)
                super(CmusRemote, self).__init__()
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
# TODO: CONFIG FILE
CMUS_CMD_KEYMAP = {
    ' ' : ('player_pause', None),
    'HOME' : ('player_pause', None),
    }

def get_options():
    parser = OptionParser()

    parser.add_option("-c", "--config-file", help="configuration file",
                      default="whitenoise_default.conf", dest="config_file")
    parser.add_option("-d", "--song-directory", help="configuration file",
                      default=".", dest="song_dir")
    parser.add_option("--debug", help="enable debugging", action="store_true",
                      default=False, dest="debug")

    cmus_group = OptionGroup(parser, "cmus replated options",
                             "These options control how the cmus remote is setup."
                             " See cmus-remote help for more info.")
    cmus_group.add_option("--cmus-server", dest="cmus_server",
                          help="cmus server", default=None)
    cmus_group.add_option("--cmus-password", dest="cmus_password",
                          help="cmus password (required when using server, "
                          "ignored otherwise)", default=None)
    cmus_group.add_option("--cmus-socket", dest="cmus_socket",
                          help="cmus socket path", default=None)
    cmus_group.add_option("--cmus-port", dest="cmus_port",
                          help="cmus port", default=3000)
    parser.add_option_group(cmus_group)

    return parser.parse_args()

def convert_key(key):
    if type(key) == str:
        if len(key) == 1:
            return ord(key)
        else:
            # First, try curses.KEY_x, e.g. KEY_UP
            if hasattr(curses, 'KEY_'+key):
                return getattr(curses, 'KEY_'+key)
            elif hasattr(curses, key):
                return getattr(curses, key)
            else:
                return int(key) # Try raw keycode; might fail :(
    else:
        return key

def normalize_keymap(raw_song_keymap, raw_cmd_keymap, song_dir):
    keymap = {}

    for char_key, song_name in raw_song_keymap.iteritems():
        keymap[convert_key(char_key)] = (CmusRemote.player_play_file,
                                         song_dir + song_name)

    # Potentially overwrites bound song keys
    for char_key, (command, args) in raw_cmd_keymap.iteritems():
        real_cmd = getattr(CmusRemote, command)
        keymap[convert_key(char_key)] = (real_cmd, args)

    return keymap

def main():
    exit_code = 0
    stdscr = None
    options = None

    try:
        (options, args) = get_options()
        cmus_keymap = normalize_keymap(SONG_KEYMAP, CMUS_CMD_KEYMAP, options.song_dir)
        remote = CmusRemote(DEFAULT_CMUS_CMD,
                            server=options.cmus_server,
                            socket_path=options.cmus_socket,
                            password=options.cmus_password,
                            port=options.cmus_port,
                            keymap=cmus_keymap)
        stdscr = curses.initscr()
        curses.noecho()

        while 1:
            c = stdscr.getch()
            print c
            if c == ord('q'):
                break
            else:
                remote.handle_key(c)

    except KeyboardInterrupt:
        if options and options.debug:
            curses.endwin()
            import pdb; pdb.set_trace()
        exit_code = 130

    finally:
        if stdscr:
            curses.endwin()

    sys.exit(exit_code)
    
if __name__ == '__main__':
    main()

