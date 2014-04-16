#!/usr/bin/python3

import json
import urllib.request
import socket
from os.path import expanduser
import os
import random
import functools

home = expanduser("~")
seenfile = home + '/' + '.reddit_seen'

def is_color_pair_readable(fg_color, bg_color):
    colors = [color % 10 for color in (bg_color, fg_color)]
    if fg_color % 10 == bg_color % 10 or (2 in colors and 6 in colors):
        return False
    return True

def add_color(in_string, color_code):
    return '\033[' + str(color_code) + 'm' + in_string + '\033[0m'

def main():
    while True:
        try:
            f = open(seenfile, 'r')
            seen = json.loads(f.read())
            f.close()
            break
        except IOError as e:
            f = open(seenfile, 'w')
            f.write('[]')
            f.close()
        except ValueError as e:
            print(seenfile + ' contains some invalid json' + '\n' + 
                    'The simplest solution is to delete it' + '\n' + 
                    '(but you will see previous top links)'
                    )
            import sys
            sys.exit(1)

    url = 'http://www.reddit.com/r/all/hot.json?limit=1'
    errors = 0
    while True:
        try:
            api_out = json.loads(urllib.request.urlopen(url).read().decode('utf8'))
            break
        except urllib.error.URLError as e:
            print('URL error', end='\r')
        except urllib.error.HTTPError as e:
            print('HTTP error', end='')
            errors = errors + 1
            if errors > 1:
                print('s x' + str(errors) + '    ', end='')
            print('\r', end='')
        except socket.gaierror as e:
            print('Socket error: ' + e[1])
    # if errors > 0: print('')

    top_link = dict()
    for key in ['id', 'url', 'title']:
        top_link[key] = api_out['data']['children'][0]['data'][key]

    if top_link['id'] not in seen:
        # style = random.choice((0, 1, 4))
        style = 1
        fg_color, bg_color = 30, 40
        while not is_color_pair_readable(fg_color, bg_color):
            fg_color = random.randrange(30, 38)
            bg_color = random.randrange(40, 48)
        print(
                functools.reduce(
                    add_color, 
                    (
                        fg_color, 
                        bg_color, 
                        style
                        ), 
                    top_link['title'] + '\n' + top_link['url'] + '\a'
                    ), 
                )
        seen.append(top_link['id'])
        f = open(seenfile, 'w')
        f.write(json.dumps(seen))
        f.close()
        os.system("echo Linky linky | festival --tts")

if __name__ == "__main__":
    main()
