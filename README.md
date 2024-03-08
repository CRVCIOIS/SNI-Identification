# SNI-code identification by NLP
This project attempts to provide pipelines and tools for training [SNI-code](https://www.scb.se/dokumentation/klassifikationer-och-standarder/standard-for-svensk-naringsgrensindelning-sni/)[^1]-predicting NLP models. 

The training toolchain can:
1. Create labeled training data by:
   1. Polling the [national statistics agency (SCB)](https://en.wikipedia.org/wiki/Statistics_Sweden)'s API.
   2. Matching URLs for every company found (if the company has a website).
   3. Automatically scraping the websites of these companies.
   4. Preprocessing the data with heuristic methods.
2. Divide the data into training-, validation- and test-sets.
3. Train a spaCy model using the datasets.

The evaluation toolchain can:
1. Scrape a single website.
2. Preprocess.
3. Use a trained model to predict the results. 

[^1]: The Swedish extension of the European [NACE](https://ec.europa.eu/eurostat/web/nace) which provides an extra level of detail compared to NACE.
## Requirements
|Pipeline command|Requirements|
|--|--|
|Common to all|MongoDB instance|
|SCB|[SCB FDB](https://www.scb.se/vara-tjanster/bestall-data-och-statistik/register/foretagsregister-och-foretagsundersokningar/foretagsdatabasen-fdb/) API credentials and certificate|
|google|[Google Custom Search JSON API credentials](https://developers.google.com/custom-search/v1/overview) and a [Google Programmable Search Engine](https://programmablesearchengine.google.com)|
|scrape|None|
|extract|None|
|divide|None|
|train-models|None|
|evaluate-accuracy-dev|None|
|evaluate-accuracy-prod|None|
## Setup
1. `pip install -r requirements.txt` (preferably inside a [Python virtual environment](https://docs.python.org/3/library/venv.html)).
2. Create a copy of `.env.example` called `.env` in the root folder, and fill in the fields.
3. Copy the SCB certificate into the root folder, and rename it to `key.pfx`.
4. Run the program using `spacy project run <workflow name>`, where `<workflow name>` should be one of the workflows from `project.yml` (i.e. `all`, `fetch`, `train`, etc.).
   - You can also create your own workflows by giving them a name and a list of commands. 
## Structure
```
NLP/
├─ adapters/        Used to abstract communication between classes, databases and files
├─ assets/          Blacklists and whitelists (.txt and .json)
├─ aux_functions/   Auxiliary functions
├─ classes/         Single-purpose classes
├─ configs/         spaCy config files
├─ pipeline/        Pipeline runner scripts
├─ tests/           
├─ UML/             
```