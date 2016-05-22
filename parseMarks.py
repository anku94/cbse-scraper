import sys, re
import json

def removeEmpty(ls):
    ls = [i for i in ls if i is not '']
    return ls

def getRecords(fname):
    f = open(fname, 'r').read().split('\n')
    f = [i.strip() for i in f if i is not '' and re.match('^\d+.*', i)]
    for idx, i in enumerate(f):
        i = i.split(' ')
        i = removeEmpty(i)
        f[idx] = i
    return f

def makeJSON(record):
    roll = record[0]
    record.pop(0)

    name = []

    while not re.match('^\d+$', record[0]):
        name.append(record[0])
        record.pop(0)

    courses = []
    while len(record) > 1 and re.match('^\d+$', record[0]):
        course = {}
        course['code'] = record[0]

        if len(record) > 3 and re.match(r'[A-Z][1-9]?', record[2]):
            record.pop(0)
            course['marks'] = record[0]
            record.pop(0)
            course['grade'] = record[0]
            record.pop(0)
        else:
            record.pop(0)

        courses.append(course)

    if len(record) > 1:
        courses.append({'code': '1001', 'marks': '100', 'grade': record[0]})
        record.pop(0)

    if len(record) > 1:
        courses.append({'code': '1002', 'marks': '100', 'grade': record[0]})
        record.pop(0)

    if len(record) > 1:
        courses.append({'code': '1003', 'marks': '100', 'grade': record[0]})
        record.pop(0)

    return {'name': ' '.join(name), 'roll': roll, 'courses': courses, 'result': record[0]}

def populate(fname):
    r = getRecords(sys.argv[1])
    for i in r[:]:
        print i
        d = makeJSON(i)
        print json.dumps(d, indent=2)


if __name__ == '__main__':
    # ls = ['3624377', 'INJAMUL', 'HAQUE', 'CHOUDHURY', '301', '039', '037', '030', '028', '048', 'ABST']
    # ls = ['1600596', 'DHARMIK', '301', '302', '041', '042', '043', 'ABST']
    # ls = ['3624575', 'ADITYA', 'KAKOTI', '301', '080', 'B1', '041', '097', 'A1', '042', '093', 'A1', '043', '095', 'A1', '048', '098', 'A1', 'A1', 'A2', 'A2', 'PASS']
    # print ls
    #d = makeJSON(ls)
    # print json.dumps(d, indent=2)
    populate(sys.argv[1])
