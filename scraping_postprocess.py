import json
import logging

# TODO: restructure into class?


def scraping_postprocess(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError):
        logging.error("Couldn't find %s!", file_path)

    restructured_json = []

    for item in data:
        for existing_item in restructured_json:
            if existing_item['domain'] == item['domain']:
                # If domain exists, append the new 'url' and 'raw_html' to
                # the 'crawled' list
                existing_item['crawled'].append({
                    "url": item['url'],
                    "raw_html": item['raw_html']
                })
                break
        else:
            # If the domain is not in restructured_json, add item to new
            # domain
            new_item = {
                "domain": item['domain'],
                "SNI": "",
                "crawled": [
                    {
                        "url": item['url'],
                        "raw_html": item['raw_html']
                    }
                ]
            }
            restructured_json.append(new_item)

    # TODO: fix output path
    with open('restructured_data.json', 'w') as f:
        json.dump(restructured_json, f, indent=4)
