import re
import requests

from random import choice
from BeautifulSoup import BeautifulSoup



UA_OPTIONS = [
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) '
     'Gecko/20071127 Firefox/2.0.0.11'),
    'Opera/9.25 (Windows NT 5.1; U; en)',
    ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; '
     '.NET CLR 1.1.4322; .NET CLR 2.0.50727)'),
    ('Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 '
     '(like Gecko) (Kubuntu)'),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 '
     'Ubuntu/dapper-security Firefox/1.5.0.12'),
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
]


class Scraper(object):
    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.headers = {'User-Agent': choice(UA_OPTIONS)} 

    def tr(self, table, index=None):
        """Scrape table rows 

        This method finds tr non-recursively 
        (BeautifulSoup.findAll is recursive by default)

        :param index: index of tr node to be returned
        :returns: table rows (tr) of the supplied table.
        """
        xs = table.findAll('tr', recursive=False)
        if index:
            return xs[index]
        return xs

    def td(self, tr, index=None):
        """Scrape table data. 

        This method finds td non-recursively 
        (BeautifulSoup.findAll is recursive by default)

        :param index: index of td node to be returned
        :returns: list of td, or td node if index supplied
        """
        xs = tr.findAll('td', recursive=False)
        if index:
            return xs[index]
        return xs

    def href(self, s, text):
        """Scrape the href of an anchor tag.

        :param text: anchor text
        :returns: href string
        """
        try:
            return s.find('a', text=text).parent['href']
        except:
            return None


    def get(self, url, params=None):
        """Returns BeautifulSoup of the content at the supplied url 
        (resolved to the BASE_URI)
        """
        url = self.resolve(url)
        response = requests.get(url, headers=self.headers, params=params)    
        return self.bs(response.content)
    
    def post(self, url, data):
        url = self.resolve(url)
        response = requests.post(url, headers=self.headers, data=data)
        return self.bs(response.content)

    def bs(self, content):
        """Returns BeautifulSoup of the supplied content (html)
        """
        return BeautifulSoup(self.strip(content))
    
    def resolve(self, uri):
        """Resolves the supplied uri relative to the BASE_URI
        """
        if uri is not None:
            if not uri.startswith('http://'):
                if uri.startswith('/'):
                    uri = '%s%s' % (self.base_uri, uri)
                else:
                    uri = '%s/%s' % (self.base_uri, uri)
            if uri.startswith(self.base_uri):
                return uri

    def strip(self, s):
        """Clean up http 'space' entities
        """
        if s is None:
            return None
        try:
            s = s.replace('&nbsp;', ' ')
            s = s.strip('\t\r\n ')
            s1 = None
            while s1 != s:
                s1 = s
                s = re.sub(r'^(\n|\r|\t)', '', s)
                s = re.sub(r'(\n|\r|\t)$', '', s)
            return s
        except Exception, e:
            print '>>>>>>>>>>>>>>', e
            return ''
