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


def handle(src, region=None):
    """Given a folder, find all xls, xlsx sheets and parse
    First sheets (0) found
    """
    if not region:
        region = fname(src)

    if os.path.isfile(src) and is_xls(src):
        lines = scan(src)
        return parse(src, lines, region)
    elif os.path.isdir(src):
        xs = []
        for f in os.listdir(src):
            path = os.path.abspath(os.path.join(src, f))
            xs.extend(handle(path, fname(src)))
        return xs

def scan(src):
    wb = open_wb(src)
    sheet = wb.sheets()[0]
    return (scan_row(sheet.row_values(i)) for i in range(sheet.nrows))

def scan_row(row):
    # try:
    if len(row) >= 3 and row[1] and row[2]:
        for p in HEADER_PATTERNS:
            if re.match(p, row[1], flags=re.I) or re.match(p, row[2], flags=re.I):
                break
        else:
            return (DATA, [' '.join(x.strip().split()) for x in row[1:3]])
    elif len(row) >= 1 and row[0]:
        m = re.match(DISTRICT_PATTERN, unicode(row[0]), flags=re.I|re.UNICODE)
        if m:
            return (DISTRICT, m.group(1).strip())
    # except Exception, e:
        # print '>>>>', e
        # raise e
        # sys.exit(1)
    return (SKIP, None) 

def parse(src, lines, region):
    """
    Assume the district name is fname (minus ext) until 
    We meet a District pattern.
    """
    
    district = fname(src)

    xs = []

    while True:
        try:
            kind, val = lines.next()

            if kind is DATA:
                xs.append([region, district] + val)
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

def fname(src):
    src = src.strip().replace('\\', '')
    while src.endswith('/'):
        src = src[:-1]
    return src.split('/')[-1].split('.')[0]

if __name__ == "__main__":
    main(sys.argv)