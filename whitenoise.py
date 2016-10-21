#!/usr/bin/env python
import os, sys
import curses # for easy input
from optparse import OptionParser, OptionGroup
from cmusbouncer import CmusBouncer
from importlib import import_module

def get_options():
    parser = OptionParser()

    parser.add_option("-c", "--config-file", help="configuration file",
                      default="config.py", dest="config_file")
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

def read_config(config_file):
    directory = os.path.dirname(config_file)
    modname = os.path.basename(config_file).rstrip('.py')
    sys.path.append(directory)
    config = import_module(modname)
    return config

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
        keymap[convert_key(char_key)] = (CmusBouncer.player_play_file,
                                         song_dir + song_name)

    # Potentially overwrites bound song keys
    for char_key, (command, args) in raw_cmd_keymap.iteritems():
        real_cmd = getattr(CmusBouncer, command)
        keymap[convert_key(char_key)] = (real_cmd, args)

    return keymap

def main():
    exit_code = 0
    stdscr = None
    options = None

    try:
        (options, args) = get_options()
        config = read_config(options.config_file)
        cmus_keymap = normalize_keymap(config.SONG_KEYMAP,
                                       config.CMD_KEYMAP,
                                       options.song_dir)
        remote = CmusBouncer(config.CMUS_CMD,
                             server=options.cmus_server,
                             socket_path=options.cmus_socket,
                             password=options.cmus_password,
                             port=options.cmus_port,
                             keymap=cmus_keymap)
        stdscr = curses.initscr()
        curses.noecho()

        while 1:
            c = stdscr.getch()
            if options.debug:
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

