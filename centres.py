"""
The Electoral Commission of Ghana is undertaking a Registration Excercise.
This is a quick hack to normalize data for designated registration centres
"""
import csv
import os
import re
import sys

from xlrd import open_workbook


DISTRICT_PATTERN = r'^\s*DISTRICT\s*:\s*(\w[\w\s\-\.]+)\s*$'

HEADER_PATTERNS = (
    r'.*ELECTORAL\s+AREA.*',
    r'.*DESIGNATE.*',
    r'.*REGISTRATION.*',
    r'.*E\s*/\s*A.*',
    r'\s+CODE[\s/]+'
)

# WB = '/home/eokyere/Desktop/EC/data/centres.xls'

DISTRICT, DATA, SKIP = range(3)

def main(args):
    data = handle(args[1])
    writer = csv.writer(sys.stdout)

    for line in data:
        writer.writerow([s.encode('utf8') for s in line])

    sys.exit(0)


def handle(src):
    """Given a folder, find all xls, xlsx sheets and parse
    First sheets (0) found
    """
    if os.path.isfile(src) and is_xls(src):
        lines = scan(src)
        return parse(src, lines)
    elif os.path.isdir(src):
        xs = []
        for f in os.listdir(src):
            path = os.path.abspath(os.path.join(src, f))
            xs.extend(handle(path))
        return xs

def scan(src):
    wb = open_wb(src)
    sheet = wb.sheets()[0]
    return (scan_row(sheet.row_values(i)) for i in range(sheet.nrows))

IC = re.IGNORECASE

def scan_row(row):
    try:
        if row[1] and row[2]:
            for p in HEADER_PATTERNS:
                if re.match(p, row[1], flags=IC) or re.match(p, row[2], flags=IC):
                    break
            else:
                return (DATA, [' '.join(x.strip().split()) for x in row[1:3]])
        elif row[0]:
            m = re.match(DISTRICT_PATTERN, row[0], flags=IC)
            if m:
                return (DISTRICT, m.group(1).strip())
    except Exception, e:
        print '>>>>', e
        sys.exit(1)
    return (SKIP, None) 

def parse(src, lines):
    """
    Assume the district name is fname (minus ext) until 
    We meet a District pattern.
    """
    
    district = src.split('/')[-1].split('.')[0]

    xs = []

    while True:
        try:
            kind, val = lines.next()

            if kind is DATA:
                xs.append([district] + val)
            elif kind is DISTRICT:
                district = val

        except StopIteration:
            break
    return xs

def open_wb(fname):
    with open(fname, 'rb') as fl:
        content = fl.read()
    return open_workbook(file_contents=content)

def is_xls(src):
    return re.match(r'^.+\.xlsx?$', src)


if __name__ == "__main__":
    main(sys.argv)