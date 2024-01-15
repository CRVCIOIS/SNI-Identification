import regex as re
from bs4 import BeautifulSoup

def extract_meta(soup):
    """
    Extracts metadata tags from a soup object
    :param soup: a soup object
    :returns: a dictionary {metadata tag: contents}
    """
    meta_tags = soup.find_all('meta')
    metadata = {}

    for tag in meta_tags:
        if 'name' in tag.attrs:
            name = tag.attrs['name']
            content = tag.attrs.get('content', '')
            metadata[name] = content
        elif 'property' in tag.attrs:  # For OpenGraph metadata
            property = tag.attrs['property']
            content = tag.attrs.get('content', '')
            metadata[property] = content

    return metadata

def extract_body(soup):
    """
    Extracts all useful parts from the body (mainly <p> tags)
    :param soup: a soup object
    :returns: a list of strings
    """
    lst = [''.join(s.findAll(string=True))for s in soup.findAll('p')]
    # TODO: find all <span> inside <pageBuilder(.*?)Text>
    #pagebuilder_tags = soup.find_all(class_=re.compile(r'pagebuilder(.*?)Text'))
    return lst

def remove_history_description(lst):
    """
    Removes strings that include 4 digits in a row, 
    in order to clean texts describing the history of the company.
    :param lst: a list of strings
    """
    year_regex = re.compile(r'\d\d\d\d')
    for index,value in enumerate(lst):
        if year_regex.search(value) is not None:
            lst.pop(index)

if __name__ == "__main__": 
    FILE_PATH = "examples/folder/file.html"

    with open(FILE_PATH, encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    
    metadata = extract_meta(soup)
    for key, value in metadata.items():
        print(f"{key}: {value}")

    body = extract_body(soup)
    remove_history_description(body)
    print(body)
