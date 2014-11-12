#!/usr/bin/env python

# parse an html page to generate a list of classes
# return newline separated list of classes
# in comma separated list

import htmlentitydefs
import re
import cgi

entity_pattern = re.compile("&(\w+?);")

def descape_entity(m, defs=htmlentitydefs.entitydefs):
    # callback: translate one entity to its ISO Latin value
    try:
        return defs[m.group(1)]
    except KeyError:
        return m.group(0) # use as is

def descape(string):
    string = re.sub(r'&nbsp;', '', string)
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
    def __init__(self, **kwargs):
        accepted = ['year', 'quarter', 'tag', 'fullname', 'instructor', 'section', 'major']
        for arg,val in kwargs.items():
            if arg in accepted:
                setattr(self, arg, val)

    def __repr__(self):
        return '{0},{1},"{2}","{3}","{4}","{5}","{6}"'.format(
                self.year, toQuarter(self.quarter), self.major, self.tag, self.section, self.fullname, self.instructor)


if __name__ == '__main__':
    import fileinput # read either file or from stdin
    s = ''
    for line in fileinput.input():
        s += line
    s = descape(s)

    instructor_regex = r'<span[^>]*?class="coursehead">(.*?)</span>.*?<span[^>]*class="fachead">(.*?)</span>'
    classname_regex = r'<td>.*?<span[^>]*class="coursehead">(.*?)</span>.*?</td>'
    major_regex = r'<td class="SAHeaderGreenBar">.*?<span[^>]*class="coursehead">(.*?)</span>.*?</td>'
    term_regex = r'<td>.*?<span id="ctl00_BodyContentPlaceHolder_detmain_lblTermHeader" class="heading2">(.*?)</span>.*?</td>'
    table_regex = r'<table[^>]*>(.*?)</table>'
    course_regex = r'^([A-Za-z ]* [A-Za-z0-9]+) (.*?)$'

    cls_re = re.compile(classname_regex, re.DOTALL)
    inst_re = re.compile(instructor_regex, re.DOTALL)
    tab_re = re.compile(table_regex, re.DOTALL)
    course_re = re.compile(course_regex)
    maj_re = re.compile(major_regex, re.DOTALL)
    term_re = re.compile(term_regex, re.DOTALL)

    table_matches = tab_re.findall(s)

    current_major = ''
    current_course = ''
    current_name = ''
    current_year = 0
    current_quarter = -1

    classes = []

    for table in table_matches:
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
            d = {'Fall': F, 'Winter': W, 'Spring':S, 'Summer':M}
            if not q or not y:
                print "shit"
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
            inst_s = (inst[0])[0]
            lec_s = (inst[0])[1]
            inst_s = inst_s.strip()
            lec_s = lec_s.strip()
            d = {'year':current_year, 'quarter':current_quarter,
                    'tag':current_course, 'fullname':current_name,
                    'instructor':inst_s, 'section':lec_s,
                    'major':current_major}
            c = Class(**d)
            classes.append(c)

    print '\n'.join([str(cls) for cls in classes])
