#!/usr/bin/env python

import urllib2
import random
import sys
import os
import time

DRY_RUN = True

def pathify(term, subject):
    return 'html/%s_%s.html' % (term, subject)

def exists(term, subject):
    return os.path.exists(pathify(term, subject))

def save(term, subject, html):
    p = pathify(term, subject)
    with open(p, 'w') as f:
        #print "writing %s" % p
        f.write(html)

def get_subjects(filename='subject_tags.dat'):
    subjects = []
    with open(filename) as f:
        for line in f:
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
    years = ['11', '12', '13', '14', '15']
    quarters = ['F', 'W', 'S']
    subjects = get_subjects()
    # 189 subjects * 5 years * 3 quarters = 2835 website hits...

    hits = 0
    max_hits = None
    max_hits = 5
    if len(sys.argv) > 1:
        max_hits = int(sys.argv[1])

    SLEEP_TIME = 3
    if len(sys.argv) > 2:
        SLEEP_TIME = int(sys.argv[2])

    for subject in subjects:
        for year in years:
            for quarter in quarters:
                term = year + quarter
                if (exists(term, subject)):
                    progress(progress.SKIP)
                    continue
                url = "http://www.registrar.ucla.edu/schedule/detmain.aspx?termsel=%s&subareasel=%s" % (term, subject)
                # yea, we're running firefox...sure...
                headers = {'User-Agent':"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}

                success = 0
                hits += 1
                if not DRY_RUN:
                    response = urllib2.urlopen(url, None, headers)
                    code = response.getcode()
                    if code == 404:
                        print "404'd!"
                        html = '' # write blank file so we don't bother trying again later
                        progress(progres.RED)
                    else:
                        html = response.read()
                        progress(progres.GREEN)
                else:
                    html = ''
                    s = random.choice([progress.RED, progress.GREEN])
                    progress(s)
                save(term, subject, html)
                if max_hits and hits >= max_hits:
                    print "\nhit %d times" % (hits)
                    sys.exit()
                time.sleep(SLEEP_TIME)
    print "\n[FINISHED] hit %d times" % (hits)

