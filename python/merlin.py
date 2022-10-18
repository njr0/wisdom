#!/usr/bin/env python3
"""merlin.py: providing access to the wisdom of Merlin Mann.

Content: Copyright (c) Merlin Mann, https://github.com/merlinmann/wisdom


Code: Copyright (c) Nick Radcliffe, Stochastic Solutions Limited, 2022
Code: MIT License.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
“Software”), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Requires Python 3.4 or later.
"""

import json
import os
import random
import sys
import time
from textwrap import wrap


WISDOM_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
while WISDOM_DIR.endswith('python'):
    WISDOM_DIR = os.path.dirname(WISDOM_DIR)
QUOTES_PATH = os.path.join(WISDOM_DIR, 'quotes.md')
WISDOM_PATH = os.path.join(WISDOM_DIR, 'wisdom.md')
JSON_PATH = os.path.join(WISDOM_DIR, 'wisdom.json')
URL = 'https://github.com/merlinmann/wisdom'

USAGE = '''
USAGE:

     python3 merlin.py            to get a piece of Merlin Mann's wisdom

     python3 merlin.py -u
  or python3 merlin.py --update   to update wisdom from after a pull.
'''



def update():
    quotes = get_quotes()
    wisdom = get_wisdom()
    wisdom['quotes'] = quotes
    with open (JSON_PATH, 'w') as f:
        json.dump(wisdom, f)


def get_quotes():
    """Read quote.md and return a list of quotes as single strings"""
    with open(QUOTES_PATH) as f:
        lines = [L.strip() for L in f.readlines()]

    # strip headings and separators
    lines = [L for L in lines if not L.startswith('#')
             and not is_separator(L)]

    quotes = []
    quote = []
    for line in lines:
        quote.append(demark(line))
        if line and is_dash(line[0]):
            quotes.append(form_quote(quote))
            quote = []
    if any(quote):
        print('WARNING: Last quote did not appear to end with an attribution',
              file=sys.stderr)
        print(repr(quote), file=sys.stderr)

    return quotes


def demark(L):
    """Strip (some) Markdown markup from line"""
    return L.replace('*', '').replace('_', '').replace('>', '').strip()


def form_quote(lines):
    """Glue the lines together and remove leading and trailing blanks"""
    return '\n'.join(lines).strip()


def get_wisdom():
    lines = get_wisdom_lines()
    wisdom = {}
    subheads = [(i, L) for i, L in enumerate(lines) if L.startswith('##')]
    for (i, section) in subheads:
        kind, content = extract_wisdom(lines[i + 1:], section)
        if kind in wisdom:
            wisdom[kind].extend(content)
        else:
            wisdom[kind] = content
    return wisdom


def extract_wisdom(lines, section):
    section = section[2:].strip()
    if section == 'Epigraphs':
        return get_epigraphs(lines, section)
    else:
        return get_general_wisdom(lines, section)


def get_epigraphs(lines, section):
    # epigraphs are separated by ----
    epigraphs = []
    epigraph = []
    for line in lines:
        if line.startswith('##'):  # next section
            break
        if not line or is_separator(line):
            continue
        if is_dash(line[0]):
            epigraph.append(demark(line))
            epigraphs.append(form_epigraph(epigraph))
            epigraph = []
        else:
            epigraph.append(demark(line))
    if epigraph:
        epigraphs.append(form_epigraph(epigraph))

    return section, epigraphs


def form_epigraph(lines):
    return '\n'.join(lines).strip()


def get_general_wisdom(lines, section):
    items = []
    for line in lines:
        if line.startswith('##'):
            break
        elif is_separator(line) or line.endswith('*The Management*'):
            pass
        elif line and is_dash(line[0]):
            items.append(demark(line[1:].strip()))
    return section, items


def get_wisdom_lines():
    """Get the main body of content from wisdom.md as a list of lines"""
    with open(WISDOM_PATH) as f:
        lines = [L.strip() for L in f.readlines()]
    # Remove everything before first subheading
    subheads = [(i, L) for i, L in enumerate(lines) if L.startswith('##')]
    if len(subheads) < 3:
        parse_failed()
    lasthead = subheads[-1][1]
    penultimate = subheads[-2][1]
    if not (lasthead.startswith('## Licensing')
            and penultimate.startswith('## About')):
        parse_failed()
    startline = subheads[0][0]
    endline = subheads[-2][0]
    lines = lines[startline:endline]
    return [L for L in lines if not L.startswith('<')
                                and not L.startswith('!')]




def parse_failed():
    """Bomb out with error, because wisdom quotes wasn't read correctly"""
    print('ERROR: Failed to parse', WISDOM_PATH, file=sys.stderr)
    sys.exit(1)


def is_separator(L):
    """
    Checks whether the line is a separator line, defined as one
    starting with ---.

    Handle the fact that there are hyphens, en-hyphens
    and em-hyphens in the files.
    """
    return len(L) >= 3 and all(is_dash(c) for c in L)


def is_dash(c):
    return c in '-–—―➖'


def check_json_exists():
    return False


def merlin():
    with open(JSON_PATH) as f:
        wisdom = json.load(f)
    random.seed(time.time() * 10000)
    n = sum(len(v) for k, v in wisdom.items())
    i = random.randint(0, n - 1)
    for k, items in wisdom.items():
        N = len(items)
        if i < N:
            lines = items[i].splitlines()
            content = ['\n'.join(wrap(L)) for L in lines]
            print('%s' % '\n'.join(content))
            print('\nFrom %s, %s\n' % (k, URL))
            sys.exit(1)
        else:
            i -= N


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) == 2 and sys.argv[1] in ('-u', '--update'):
            update()
        else:
            print(USAGE, file=sys.stderr)
            sys.exit(1)

    if not os.path.exists(JSON_PATH):
        update()
    merlin()

