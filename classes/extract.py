"""
Extracts information from scraped websites, 
to reduce noise in AI model training.
"""
import logging

import regex as re
from bs4 import BeautifulSoup


class NoBeautifulSoupObject(Exception):
    """
    Data extractor hasn't generated a BeautifulSoup object, and cannot start extracting data.
    """
    pass

class DataExtractor:
    """
    Extracts information from scraped websites.
    """
    def __init__(self):
        self.soup = None
        self.string_filter_list = [ # Last filter, removes strings from lists.
            re.compile(r'\d\d\d\d') # Remove strings with years (i.e. a string containing '2013')
            ]

        self.character_filter_list = [ # Last filter, removes characters from strings.
            re.compile(r'\s{2,}'),  # Remove multiple spaces
            re.compile(r'\|+'),     # Remove pipes
            re.compile(r'\n+'),     # Remove newlines
            re.compile(r'\t+'),     # Remove tabs
            re.compile(r'\r+'),     # Remove carriage returns
            re.compile(r"#\w+"),    # Remove hashtags
            re.compile("["          # Remove emojis and other symbols
                u"\U0001F600-\U0001F64F"  
                u"\U0001F300-\U0001F5FF"  
                u"\U0001F680-\U0001F6FF"  
                u"\U0001F1E0-\U0001F1FF"  
                u"\U00002702-\U000027B0"
                u"\U000024C2-\U0001F251"
                u"\U0001f926-\U0001f937"
                u"\U00010000-\U0010ffff"
                u"\u2640-\u2642" 
                u"\u2600-\u2B55"
                u"\u200d"
                u"\u23cf"
                u"\u23e9"
                u"\u231a"
                u"\ufe0f"
                u"\u3030"
                "]+", flags=re.UNICODE)
        ]


    def __str__(self):
        return self.extract()

    def open_file(self, file_path):
        """
        Opens a file and creates a soup object from a file.
        :param file_path: path to an html file.
        """
        try:
            with open(file_path, encoding='utf-8') as fp:
                self.create_soup_from_string(fp)
        except (FileNotFoundError):
            logging.error("Couldn't find %s!", file_path)
    
    def create_soup_from_string(self, raw_html):
        """
        Creates a soup object from a raw HTML string or a file pointer.
        :raw_html: raw HTML string or a file pointer.
        """
        try:
            self.soup = BeautifulSoup(raw_html, 'html.parser')
        except (TypeError, AttributeError, AssertionError) as e:
            logging.error(e)
            self.soup = None

    def extract(self, filter_ = True, p_only = False, extract_meta = True, extract_body = True):
        """
        Extracts text and creates a string from a scraped HTML page.
        :param filter_: if True (default), then the data is also filtered.
        :param p_only: if True, then only paragraphs will be scraped from the body.
        :param extract_meta: if True, then meta will be extracted.
        :param extract_body: if True, then body will be extracted. 
        :returns: a string
        """
        s = ""
        
        if (extract_body or p_only):
            body = self._extract_body(filter_, p_only)
            if filter_:
                self._filter_list(body)
                body = list(set(body))  # remove duplicates
            for item in body:
                s += item + " "
            
        if extract_meta:
            meta = self._extract_meta(filter_)
            if filter_:
                meta = list(set(meta))  # remove duplicates
            for item in meta:
                s += item + " "
                
        if filter_:
            s = self._filter_chars(s)
        return s
    
    def extract_simple_data(self):
        """
        Find links for telephone numbers and e-mail addresses in a website.
        :returns: a dictionary of lists of strings {'tel': [], 'email': []}
        """
        results = {}
        results['tel'] = [tel.replace('-', '').replace(' ', '') for tel in set(self._extract_from_href('tel'))]
        results['email'] = list(set(self._extract_from_href('mailto')))
        
        return results
    
    def _extract_from_href(self, keyword):
        """
        Return a list of strings [s] where a href contains the keyword:
            <a href="keyword:s">...</a>
        :param keyword: the keyword to be searched
        :returns: a list of strings
        """
        if self.soup is None:
            raise NoBeautifulSoupObject
        results = []
        href_regex = re.compile(fr'{keyword}:(.*)')

        all_tags = self.soup.find_all('a', href=lambda href: href and keyword in href)
        for tag in all_tags:
            match = href_regex.match(tag.get('href'))
            if match:
                results.append(match.group(1))
        return results

    def _extract_meta(self, filter_=True):
        """
        Extracts text from the metadata of a scraped HTML page.
        :param filter_: if True (default), then the data is also filtered 
        (only title and description are kept).
        :returns: a dictionary {metadata tag: contents}
        """
        if self.soup is None:
            raise NoBeautifulSoupObject

        
        allowed_tags = ['title','description']

        meta_tags = self.soup.find_all('meta')
        metadata = []

        for tag in meta_tags:
            name = None
            if 'name' in tag.attrs:
                name = tag.attrs['name']
            elif 'property' in tag.attrs:  # For OpenGraph metadata
                name = tag.attrs['property']
            else:
                continue
            if filter_:
                for allowed_tag in allowed_tags:
                    if allowed_tag in name:
                        content = tag.attrs.get('content', '')
                        metadata.append(content)
                        break
            else:
                content = tag.attrs.get('content', '')
                metadata.append(content)


        return metadata

    def _extract_body(self, filter_=True, p_only=False):
        """
        Extracts text from the body of a scraped HTML page.
        :param filter_: if True (default), then the data is also filtered 
        (removes links and cookies).
        :param p_only: if True, then only paragraphs (<p> tags) will be extracted.
        :returns: a list of strings.
        """
        if self.soup is None:
            raise NoBeautifulSoupObject

        
        if filter_:
            # Remove links
            for element in self.soup.find_all('a'):
                if element.strings is not None:
                    element.decompose()
            # Remove tags containing "cookie"
            for element in self.soup.find_all('div', class_=re.compile("cookie*.")):
                element.decompose()
            # Remove JS scripts    
            for element in self.soup.find_all('script'):
                element.decompose()

        if p_only:
            lst = [''.join(s.findAll(string=True))for s in self.soup.findAll('p')]
        else:
            lst = [s for s in self.soup.stripped_strings]
        return lst

    def _filter_list(self, lst):
        """
        Takes a list of strings and removes every string 
        with a matching regex from the filter list.
        :param lst: a list of strings
        """
        for i,value in enumerate(lst):
            for filt in self.string_filter_list:
                if filt.match(value):
                    lst.pop(i)
                    
    def _filter_chars(self, text):
        """
        Takes a string and removes every character 
        with a matching regex from the filter list.
        :param text: a string
        """
        for filter in self.character_filter_list:
            text = filter.sub('', text) 
        return text
