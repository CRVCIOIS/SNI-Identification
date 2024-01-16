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
    Extracts all text from the body of a soup object
    :param soup: a soup object
    :returns: a list of strings
    """
    # TODO: dynamic regex based tag filtering
    body_text_lst = []

    queue = [([], soup.body)]
    while queue:
        path, element = queue.pop(0)
        if hasattr(element, 'children'): 
            for child in element.children:
                queue.append((path + [child.name if child.name is not None else type(child)],
                            child))
        else:
            text = element.get_text(separator=' ', strip=True)
            if text != '':
                body_text_lst.append(text)

    return body_text_lst

def extract_header(soup):
    pass


if __name__ == "__main__":
    FILE_PATH = "examples/bdx/bdx.html"

    with open(FILE_PATH, encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    
    metadata = extract_meta(soup)
    for key, value in metadata.items():
        for s in ['title', 'description']:
            if s in key:
                print(f"{key}: {value}")

    body = extract_body(soup)
    print(body)
