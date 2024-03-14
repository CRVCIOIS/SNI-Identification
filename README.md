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

### Commands

The following commands are defined by the project.
Commands are only re-run if their inputs have changed.

| Command | Description | Requirements 
| --- | --- | --- |
| `SCB` | Get data from SCB | [SCB FDB](https://www.scb.se/vara-tjanster/bestall-data-och-statistik/register/foretagsregister-och-foretagsundersokningar/foretagsdatabasen-fdb/) API credentials and certificate & MongoDB instance|
| `google` | Fill the DB with a matching URL for each company by using Google search API | [Google Custom Search JSON API credentials](https://developers.google.com/custom-search/v1/overview) and a [Google Programmable Search Engine](https://programmablesearchengine.google.com) & MongoDB instance|
| `scrape` | Scrapes websites |  |
| `extract` | Extracts the valuable data from the scraped website | MongoDB instance|
| `divide` | Divides the dataset into training and validation sets | MongoDB instance|
| `preprocess` | Convert the data to spaCy's binary format | MongoDB instance|
| `train-models` | Train a text classification model | MongoDB instance|
| `evaluate-accuracy-prod` | Evaluate the prod model for accuracy and export metrics | |
| `evaluate-speed-prod` | Evaluate the prod model for speed and export metrics | |
| `evaluate-accuracy-dev` | Evaluate the dev model for accuracy and export metrics | |
| `evaluate-speed-dev` | Evaluate the dev model for and export metrics | |
| `predict` | Predict the SNI code of a company based on their website data | |
| `eval-custom` | Custom evaluation of the model | |

###  Workflows

The following workflows are defined by the project. They
can be executed using `spacy project run [workflow]`
and will run the specified commands in order. Commands are only re-run if their
inputs have changed.

| Workflow | Steps |
| --- | --- |
| `evaluate-dev` | `evaluate-accuracy-dev` |
| `evaluate-prod` | `evaluate-accuracy-prod` |
| `all` | `SCB` &rarr; `google` &rarr; `scrape` &rarr; `extract` &rarr; `divide` &rarr; `preprocess` &rarr; `train-models` |
| `fetch` | `SCB` &rarr; `google` &rarr; `scrape` |
| `train` | `extract` &rarr; `divide` &rarr; `preprocess` &rarr; `train-models` |
| `test_without_training` | `extract` |

## Setup
1. `pip install -r requirements.txt` (preferably inside a [Python virtual environment](https://docs.python.org/3/library/venv.html)).
2. Create a new Google search engine, and add all URLs from `assets/google_search_blacklist.txt` to the engine blacklist.
3. Create a copy of `.env.example` called `.env` in the root folder, and fill in the fields.
   - `GOOGLE_SEARCH_API_KEY` is gathered from [Google Custom Search JSON API credentials](https://developers.google.com/custom-search/v1/overview)
   - `GOOGLE_SEARCH_ENGINE_ID` is gathered from [Google Programmable Search Engine](https://programmablesearchengine.google.com)
   - `SCB_API_USER` & `SCB_API_PASS` is gathered from your SCB account that you get issued when signing a contract with SCB for [SCB FDB](https://www.scb.se/vara-tjanster/bestall-data-och-statistik/register/foretagsregister-och-foretagsundersokningar/foretagsdatabasen-fdb/)
4. Copy the SCB certificate into the root folder, and rename it to `key.pfx`.
5. Run the program using `spacy project run <workflow name>`, where `<workflow name>` should be one of the workflows from `project.yml` (i.e. `all`, `fetch`, `train`, etc.).
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
