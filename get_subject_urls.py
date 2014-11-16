#!/usr/bin/env python

import urllib2
import re

#http://www.registrar.ucla.edu/schedule/catsel.aspx
course_regex_s = r'<a href="catalog\.aspx\?sa=([^&]*)&funsel=3">'
course_regex = re.compile(course_regex_s)

url = "http://www.registrar.ucla.edu/schedule/catsel.aspx"
headers = {'User-Agent':"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}

req = urllib2.Request(url, None, headers)
response = urllib2.urlopen(req)

s = response.read()

matches = course_regex.findall(s)
with open('subject_tags.dat', 'w') as f:
    for match in matches:
        f.write(match+'\n')
