"""
The Electoral Commission of Ghana's website has a list of all the polling stations
in Ghana. This is a quick hack to free that data into a CSV.

"""

import csv
import os
import re
import sys

import helper


def main(args):
    scraper = Stations('http://www.ec.gov.gh')
    data = scraper.scrape()
    write_csv(sort(data))
    sys.exit(0)

def write_csv(data, target=None):
    writer = csv.writer(target or sys.stdout)
    for line in data:
        writer.writerow([s.encode('utf8') for s in line])

def sort(data):
    f = lambda a, b: a + b
    return sorted(data, key=lambda x: reduce(f, [s.lower() for s in x]))


class Stations(helper.Scraper):
    def scrape(self):
        """Scrape the values from the EC site.
        """
        values = []

        for _, rid in self.regions():
            for _, did in self.districts(rid):
                for _, cid in self.constituencies(did):
                    values.extend(self.data(rid, did, cid))
        return values

    def data(self, region, district, constituency):
        """To get polling stadion data, the EC site will send the ff POST.

        3. POST http://www.ec.gov.gh/poll.php 
           data=dict(drop_1=<region-val>, 
                     drop_2=<district-val>,
                     drop_3=<constituency-val>,
                     submit='Submit')    
        """
        data = dict(drop_1=region, drop_2=district, 
                    drop_3=constituency, submit='Submit')
        soup = self.post('/poll.php', data=data)
        
        # div text format Region | District | Constituency (<total> Polling stations)
        div = soup.find('div', attrs={'class': 'content_text_column'}).text
        div = [s.strip() for s in div.split('(')[0].strip().split('|')]

        table = soup.find('table', attrs={'id':'summ_table'})
        trs = table.findAll('tr')[1:] # leave out the header
        return [location + [td.text.strip() for td in tr.findAll('td')] for tr in trs]

    def regions(self):
        # We are hardcoding this for now
        # s = """
        # <select name="drop_1" id="drop_1">
        # <option value="" selected="selected" disabled="disabled">Select Region</option>
        # <option value="1">Ashanti</option><option value="2">Brong Ahafo</option>
        # <option value="3">Central</option>
        # <option value="4">Eastern</option>
        # <option value="5">Greater Accra</option>
        # <option value="6">Northern</option>
        # <option value="7">Western</option>
        # <option value="8">Volta</option>
        # <option value="9">Upper West</option>
        # <option value="10">Upper East</option>    
        # </select>
        # """ 
        # return self.options(self.bs(s))
        names = ('Ashanti', 'Brong Ahafo', 'Central', 'Eastern', 'Greater Accra', 
                 'Northern', 'Western', 'Volta', 'Upper West', 'Upper East')
        return (zip(names, [str(x) for x in range(1, 11)]))

    def districts(self, region_id):
        """Get the list of districts within a specific region.

        :param: region_id - the region the districts belong to.
        """
        return self.func(dict(func='drop_1', drop_var=region_id))

    def constituencies(self, district_id):
        """Get the list of constituencies within a specific district.

        :param: district_id - the district the constituencies belong to.
        """
        return self.func(dict(func='drop_2', drop_var=district_id))

    def func(self, params):
        """
        The drop downs on the EC poll page make the ff requests:

        1. GET http://www.ec.gov.gh/func.php?func=drop_1&drop_var=<region-val>
        2. GET http://www.ec.gov.gh/func.php?func=drop_2&drop_var=<district-val>
        """        
        soup = self.get('/func.php', params=params)
        return self.options(soup)

    def options(self, select):
        """Extract option (text, value) tuptles 
        """
        return [(x.text.strip(), x['value']) for x in select.findAll('option')][1:]


if __name__ == "__main__":
    main(sys.argv) 