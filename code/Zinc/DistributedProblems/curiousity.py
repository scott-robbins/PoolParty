import numpy as np
import requests
import utils
import time
import sys
import os


def web_search(l, verbose):
    link = 'https://en.wikipedia.org/wiki/'+l.replace(' ', '_')
    DATA = {}
    links = []
    children = []
    if verbose:
        print '\033[3m Searching for %s\033[0m' % link
    data = requests.get('%s' % (link.replace(' ', '_')))
    headers = data.headers
    cookies = data.cookies
    content = data.content.split('<p>')
    if verbose:
        print 'Headers: %s' % headers
        print 'Cookies: %s' % cookies
        print '%ss Elapsed' % data.elapsed
    print '%d paragraphs received' % len(content)
    for P in range(1, len(content), 1):
        para = content[P]
        DATA[P] = []
        for element in para.split(' '):
            if len(element.split('href=')) > 1:
                links.append(element.split('href=')[1])
    if verbose:
        print '%d Embedded Links in Article' % len(links)
        print '=========================================================='
        print content[1:3]

    # Recursively crawl links, as child of current link
    for l in links:
        if len(l.split('"/wiki/')) > 1:
            children.append(l)
    DATA['Links'] = children
    DATA['Headers'] = headers
    DATA['Cookies'] = cookies

    # TODO: FOR DEBUGGING
    file_name = '%s.txt' % link.split('.org/wiki/')[1].replace(' ','_')
    print 'Dumping to LogFile %s' % file_name
    os.system('touch %s' % file_name)
    dump = ''
    for par in content[1:]:
        for line in par.split('\n'):
            dump += line + '\n'
    open(file_name, 'w').write(dump)
    print '%s Bytes of RAW HTML DUMPED' % os.path.getsize(file_name)
    return DATA


if '-s' in sys.argv and len(sys.argv) >= 3:
    results = web_search(sys.argv[2], True)
