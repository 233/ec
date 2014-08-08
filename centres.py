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
    r'.*ELECTORAL.*',
    r'.*DESIGNATE.*',
    r'.*REGISTRATION.*',
    r'.*E\s*/\s*A.*',
    r'\s+CODE[\s/]+'
)

DISTRICT, DATA, SKIP = range(3)


def main(args):
    data = handle(args[1])
    writer = csv.writer(sys.stdout)

    f = lambda a, b: a + b
    data = sorted(data, key=lambda x: reduce(f, [s.lower() for s in x]))

    for line in data:
        writer.writerow([s.encode('utf8') for s in line])

    sys.exit(0)


def handle(src, region=None, depth=0, limit=0):
    """Given a source, if it is an xls(x) file, parse it.
    If it is a folder, find all xls(x) files and parse them.
    """
    if not region:
        region = fname(src)

    region = region.title()

    if os.path.isfile(src) and is_xls(src):
        return parse(scan(src), region, fname(src).title())
    elif os.path.isdir(src) and depth <= limit:
        xs = []
        depth += 1
        for f in os.listdir(src):
            path = os.path.abspath(os.path.join(src, f))
            xs.extend(handle(path, fname(src), depth, limit))
        return xs
    return []

def scan(src):
    """Analyze all rows of the workbook to determine which rows to extract 
    data from.

    :param: src - the filename fo the Excel sheet to scan
    :return: Returns a generator of (kind, value) tuples
    """
    wb = open_wb(src)
    sheet = wb.sheets()[0]
    return (scan_row(sheet.row_values(i)) for i in range(sheet.nrows))

def scan_row(row):
    """Analyze a row to determine whether we should parse it, and what kind of row it is.

    :param: row - Row values from Excel sheet
    :return: Returns a tuple of (kind, value) -- kinds: DISTRICT, DATA, SKIP
    """
    try:
        if len(row) >= 3 and row[1] and row[2]:
            for p in HEADER_PATTERNS:
                if re.match(p, row[1], flags=re.I) or re.match(p, row[2], flags=re.I):
                    break
            else:
                return (DATA, [' '.join(x.strip().split()) for x in row[1:3]])
        elif len(row) >= 1 and row[0]:
            m = re.match(DISTRICT_PATTERN, unicode(row[0]), flags=re.I|re.UNICODE)
            if m:
                return (DISTRICT, m.group(1).strip().title())
    except Exception, e:
        print '>>>>', e
        # sys.exit(1)
    return (SKIP, None) 

def parse(rows, region, district):
    """Parse the given rows to extract centres data.

    :param: rows - Generator of (kind, value) tuples to parse
    :param: region
    :param: district
    """

    data = []

    while True:
        try:
            kind, val = rows.next()

            if kind is DATA:
                data.append([region, district] + val)
            elif kind is DISTRICT:
                district = val
        except StopIteration:
            break
    return data

def open_wb(fname):
    """Open workbook.
    """
    with open(fname, 'rb') as fl:
        content = fl.read()
    return open_workbook(file_contents=content)

def is_xls(src):
    """Returns True if src is an Excel file (xls/xlsx).
    """
    return re.match(r'^.+\.xlsx?$', src)

def fname(src):
    """Returns the filename or folder name of src.
    """
    src = src.strip().replace('\\', '')
    while src.endswith('/'):
        src = src[:-1]
    return src.split('/')[-1].split('.')[0]

if __name__ == "__main__":
    main(sys.argv)