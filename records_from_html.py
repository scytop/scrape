#!/usr/bin/env python

# parse an html page to generate a list of classes
# return newline separated list of classes
# in comma separated list

import htmlentitydefs
import re
import cgi
import sys

entity_pattern = re.compile("&(\w+?);")

def progress(count, l, length=40, COL='\033[32m', skip=5):
    '''
    print progress bar, length characters long,
    in COL (ansi escape color sequence)
    with position count/l
    only print every skip times called
    '''
    progress.current += 1
    if progress.current < skip:
        return # don't write every time
    progress.current = 0
    l = l-1
    p = int((float(count) / l) * length)
    done = '=' * p
    notdone = ' ' * (length - p)
    CLR = '\033[0m'
    s = "[%s%s%s%s] %06d/%06d" % (COL, done, CLR, notdone, count, l)
    sys.stderr.write('\033[0G')
    sys.stderr.flush()
    sys.stderr.write(s)
progress.current = 0

def descape_entity(m, defs=htmlentitydefs.entitydefs):
    '''
    callback: translate one entity to its ISO Latin value
    '''
    try:
        return defs[m.group(1)]
    except KeyError:
        return m.group(0) # use as is

def descape(string):
    string = re.sub(r'&nbsp;', '', string) # don't need tabs
    return entity_pattern.sub(descape_entity, string)

F = 0
W = 1
S = 2
M = 3 # summer
def toQuarter(q):
    if q == F:
        return 'F'
    elif q == W:
        return 'W'
    elif q == S:
        return 'S'
    elif q == M:
        return 'M'
    else:
        return 'Q'


class Class:
    accepted = ['year', 'quarter', 'tag', 'fullname', 'instructor', 'section', 'major']
    longest = {i: 0 for i in accepted}
    def __init__(self, **kwargs):
        for arg,val in kwargs.items():
            if arg in self.accepted:
                if type(val) == str:
                    val = re.sub(' +|\t', ' ', val).strip() # replace multiple spaces or a tab with a space
                    if len(val) > self.longest[arg]:
                        self.longest[arg] = len(val)
                setattr(self, arg, val)

    def __repr__(self):
        return '{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(
                self.year, toQuarter(self.quarter), self.major, self.tag, self.fullname, self.instructor)

    @classmethod
    def fields(cls):
        return 'year\tquarter\tsubject\ttag\tname\tinstructor'

    @classmethod
    def get_longest(cls):
        s = 'longest:     '
        for key, val in cls.longest.items():
            s += '%s: %d\t' % (key, val)
        return s


if __name__ == '__main__':
    import fileinput # read either file or from stdin
    s = ''
    sys.stderr.write('[Reading input]\n') # stderr so that simple stdout redirect is easy and unaffected
    for line in fileinput.input():
        s += line
    s = descape(s)

    instructor_regex = r'<span[^>]*?class="coursehead">(.*?)</span>.*?<span[^>]*class="fachead">(.*?)</span>'
    classname_regex = r'<td>.*?<span[^>]*class="coursehead">(.*?)</span>.*?</td>'
    major_regex = r'<td class="SAHeaderGreenBar">.*?<span[^>]*class="coursehead">(.*?)</span>.*?</td>'
    term_regex = r'<td>.*?<span id="ctl00_BodyContentPlaceHolder_detmain_lblTermHeader" class="heading2">(.*?)</span>.*?</td>'
    table_regex = r'<table[^>]*>(.*?)</table>'
    course_regex = r'^([A-Za-z &]* [A-Za-z0-9]+) (.*?)$'

    cls_re = re.compile(classname_regex, re.DOTALL)
    inst_re = re.compile(instructor_regex, re.DOTALL)
    tab_re = re.compile(table_regex, re.DOTALL)
    course_re = re.compile(course_regex)
    maj_re = re.compile(major_regex, re.DOTALL)
    term_re = re.compile(term_regex, re.DOTALL)

    sys.stderr.write('[Matching table groups]\n')
    table_matches = tab_re.findall(s)

    current_major = ''
    current_course = ''
    current_name = ''
    current_year = 0
    current_quarter = -1

    classes = []

    sys.stderr.write('[Matching courses]\n')
    l = len(table_matches)
    for i,table in enumerate(table_matches):
        progress(i, l)
        cls = cls_re.findall(table)
        inst = inst_re.findall(table)
        maj = maj_re.findall(table)
        term = term_re.findall(table)

        if (maj):
            maj_s = maj[0]
            current_major = maj_s
        if (term):
            term_s = term[0]
            q = re.findall(r'(Fall|Spring|Summer|Winter)', term_s)
            y = re.findall(r'(201[0-9])', term_s)
            # sure, python2.7 has enums
            d = {'Fall': F, 'Winter': W, 'Spring':S, 'Summer':M}
            assert(q and y)
            current_quarter = d[q[0]]
            current_year = y[0]
        if (cls):
            cls_s = cls[0]
            course = course_re.findall(cls_s)
            if len(course):
                course_s = course[0][0].strip()
                title_s = course[0][1].strip()
                current_course = course_s
                current_name = title_s
        if (inst):
            inst_s = (inst[0])[1]
            lec_s = (inst[0])[0]
            inst_s = inst_s.strip()
            lec_s = lec_s.strip()
            d = {'year':current_year, 'quarter':current_quarter,
                    'tag':current_course, 'fullname':current_name,
                    'instructor':inst_s, 'section':lec_s,
                    'major':current_major}
            c = Class(**d)
            classes.append(c)

    print Class.fields()
    print '\n'.join([str(cls) for cls in classes])
    sys.stderr.write('\n' + Class.get_longest())
