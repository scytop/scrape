#!/usr/bin/env python

import urllib2
import random
import sys
import os
import time
import signal
import re

DRY_RUN = False

def signal_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def pathify(term, subject):
    return '%s/%s_%s.html' % (pathify.pref, term, subject)
pathify.pref = 'html'

def exists(term, subject):
    return os.path.exists(pathify(term, subject))

def save(term, subject, html):
    p = pathify(term, subject)
    with open(p, 'w') as f:
        f.write(html)

def get_subjects(filename='subject_tags.dat'):
    subjects = []
    with open(filename) as f:
        for line in f:
            line = re.sub(r'%26', r'&', line)
            subjects.append(line.strip())
    return subjects

def progress(color=0):
    if progress.l > 80:
        sys.stdout.write('\n')
        progress.l = 0
    if color == progress.GREEN:
        COL = '\033[32m' # green
        CLR = '\033[0m'
        sys.stdout.write(COL + '*' + CLR)
    elif color == progress.RED:
        COL = '\033[31m' # red
        CLR = '\033[0m'
        sys.stdout.write(COL + '*' + CLR)
    else: # progress.skip
        sys.stdout.write('.')
    sys.stdout.flush()
    progress.l += 1
progress.l = 0
progress.RED = 0
progress.GREEN = 1
progress.SKIP = -1

if __name__ == '__main__':
    years = ['14']
    quarters = ['F', 'W', 'S']
    subjects = get_subjects()

    if not os.path.exists(pathify.pref):
        os.makedirs(pathify.pref)

    hits = 0
    prog = 0

    max_hits = 10
    SLEEP_TIME = 6

    import argparse
    parser = argparse.ArgumentParser(description='Scrape UCLA for schedule of classes data. Save html files to html directory')
    parser.add_argument('-s', type=float, metavar='sleep-time', help='Set sleep time between requests')
    parser.add_argument('-n', type=int, metavar='max-requests', help='Set maximum number http requests sent')
    parser.add_argument('-q', type=str, metavar='quarters', help='Set which quarters to scrape')
    parser.add_argument('-y', type=str, metavar='year', help='Set which year to scrape')
    args = parser.parse_args()

    s = args.s
    n = args.n
    q = args.q
    y = args.y
    if s:
        SLEEP_TIME = s
    if n:
        max_hits = n
    if q:
        quarters = []
        if 'F' in q:
            quarters += 'F'
        if 'W' in q:
            quarters += 'W'
        if 'S' in q:
            quarters += 'S'
    if y:
        if len(y) == 4:
            y = y[2:] # not 2014, just 14
        years = [y]

    for subject in subjects:
        for year in years:
            for quarter in quarters:
                prog += 1
                term = year + quarter
                # file exists means we've tried it before
                if (exists(term, subject)):
                    progress(progress.SKIP)
                    continue
                url = "http://www.registrar.ucla.edu/schedule/detmain.aspx?termsel=%s&subareasel=%s" % (term, subject)
                headers = {'User-Agent':"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}

                success = 0
                hits += 1
                if not DRY_RUN:
                    req = urllib2.Request(url, None, headers)
                    try:
                        response = urllib2.urlopen(req)
                    except Exception as e:
                        progress(progress.RED)
                        print "\nUrl access failed!"
                        print "\nhit %d times, %d left" % (hits, len(years)*len(quarters)*len(subjects) - prog)
                        sys.exit()
                    code = response.getcode()
                    if code == 404:
                        html = '' # write blank file so we don't bother trying again later
                        progress(progress.RED)
                    else:
                        html = response.read()
                        progress(progress.GREEN)
                else:
                    html = ''
                    progress(progress.RED)
                save(term, subject, html)
                if max_hits and hits >= max_hits:
                    print "\nhit %d times, %d left" % (hits, len(years)*len(quarters)*len(subjects) - prog)
                    sys.exit()
                time.sleep(SLEEP_TIME)
    print "\n[FINISHED] hit %d times. Got %s for %s" % (hits, ', '.join(quarters), ', '.join(years))

