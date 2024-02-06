import json
import logging
from pathlib import Path


class ScrapingPostprocess:
    """
    Class for postprocessing the scraped data.
    
    :param file_path: path to the file with the scraped data.
    :param output_directory: path to the directory where the restructured data will be saved.
    """
    def __init__(self, file_path, output_directory):
        self.file_path = file_path
        self.output_directory = output_directory
        self.input_data = None
        
    def _open_file(self):
        """
        Opens a file and loads the data into a dictionary.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.input_data = json.load(f)
        except (FileNotFoundError):
            logging.error("File not found: %s", self.file_path)
        except json.JSONDecodeError:
            logging.error("File is not a valid JSON file: %s", self.file_path)

    def postprocess(self):
        """
        Postprocesses the scraped data into desired structure.
        """
        self._open_file()
        restructured_json = []
        
        if self.input_data is not None:
            for item in self.input_data:
                for existing_item in restructured_json:
                    if existing_item['domain'] == item['domain']:
                        # If domain exists, append 'url' and 'raw_html' to
                        # the 'crawled' list
                        existing_item['crawled'].append({
                            "url": item['url'],
                            "raw_html": item['raw_html']
                        })
                        break
                # If the domain is not in restructured_json, add item to new
                # domain
                else:
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
                            
            self._write_to_file(restructured_json)

    def _write_to_file(self, restructured_json):
        """
        Writes the restructured data to a file.
        :param restructured_json: restructured data
        """
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)
        file_name = Path(self.file_path).name
        with open(f'{self.output_directory}/{file_name}','w', encoding='utf-8') as fp:
            json.dump(restructured_json, fp, indent=4)
        logging.info("Data written to %s", self.output_directory)


#ScrapingPostprocess(r"scraping\NLPspider\data\crawlingNLP\crawlingNLP_2024-02-06T09-00-10+00-00.json", r"scraping\NLPspider\restructured_data").postprocess()