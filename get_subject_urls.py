#!/usr/bin/env python

import re

#http://www.registrar.ucla.edu/schedule/catsel.aspx

course_regex_s = r'<a href="catalog\.aspx\?sa=([^&]*)&funsel=3">'
course_regex = re.compile(course_regex_s)

with open('all_subjects.html') as f:
    s = f.read()

matches = course_regex.findall(s)
with open('subject_tags.dat', 'w') as f:
    for match in matches:
        f.write(match+'\n')
