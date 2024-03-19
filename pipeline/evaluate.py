import typer
import logging
import spacy
from pathlib import Path
from typing_extensions import Annotated
from adapters.train import TrainAdapter


def evaluation(predictions: dict, true_label: str, top_n: int) -> dict:
    """
    Evaluate the model predictions on a data point.
    
    :param predictions (dict): the models predictions for the data point
    :param true_label (str): the true label for the data point
    :param top_n (int): the number of top predictions to evaluate
    :return (dict): a dictionary with the results of the evaluation
    """
    results = {}
    sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
    logging.debug(f"Predictions: {sorted_predictions[0:top_n]}")
    logging.debug(f"True label: {true_label}")     

    for i,(label, _) in enumerate(sorted_predictions):
        if is_correct_label(label, true_label):
                if i == 0:
                    results['correct_label'] = 1
                    logging.debug("Correct label!")
                if i < top_n:
                    results[f'top_{top_n}_label'] = 1

        if is_correct_category(label, true_label):
            if i == 0:
                results['correct_category'] = 1
                logging.debug("Correct category!")
            if i < top_n:
                results[f'top_{top_n}_category'] = 1
            results['weighted_category_score'] = 1 * (1/(i+1))
            
    return {'label': true_label, 'results': results}

def is_correct_label(label: dict, true_label: dict) -> bool:
    """Returns True if the label is correct."""
    return label == true_label

def is_correct_category(label: dict, true_label: dict) -> bool:
    """Returns True if the category is correct."""
    return label[:2] == true_label[:2]

def load_data_and_model(model_path: Path) -> tuple[list, spacy.language.Language]:
    """
    Load test data and model
    
    :param model_path (Path): the path to the model
    :return (list,spacy.language.Language): the test data and the model
    """
    train_adapter = TrainAdapter()
    test_data = [company for company in train_adapter.fetch_test_set()]
    nlp = spacy.load(model_path)
    return test_data, nlp

def update_label_results(total_results: dict, point_results: dict) -> dict:
    """
    Update total results with the results from the current data point.
    
    :param total_results (dict): the total results so far
    :param point_results (dict): the results from the current data point
    :return (dict): the updated total results
    """
    if point_results['label'] not in total_results:
        total_results[point_results['label']] = point_results['results']
    else:
        for key in point_results['results']:
            total_results[point_results['label']][key] = total_results[point_results['label']].get(key, 0) + point_results['results'][key]
    if 'skipped' not in point_results['results'].keys():
        total_results[point_results['label']]['label_count'] = total_results[point_results['label']].get('label_count', 0) + 1
    return total_results

def calculate_total_results(results: dict) -> dict:
    """ 
    Calculate the total results from the label results.
    
    :param results (dict): the results per label
    :return (dict): the total results
    """
    total_results = dict()
    for label in dict(sorted(results.items())):
        for key in results[label]:
            total_results[key] = total_results.get(key, 0) + results[label].get(key, 0)
        total_results['total_items'] = total_results.get('total_items', 0) + results[label].get('label_count', 0)
    return total_results

def get_percentage(correct: int, total: int) -> float:
    """ 
    Get the percentage of correct predictions.
    
    :param correct (int): the number of correct predictions
    :param total (int): the total number of predictions
    :return (float): the percentage of correct predictions
    """
    return round(correct/total*100, 3)

def log_results(results: dict, top_n: int):
    """
    Log the results of the evaluation. Results are logged per label and total.
    
    :param results (dict): the results of the evaluation
    :param top_n (int): the number of top predictions to evaluate
    """
    total_results = calculate_total_results(results)
    logging.info(f"Results per label:")
    for label in dict(sorted(results.items())):
        logging.info(
            f"Label {label}: "
            f"Correct label: {get_percentage(results[label].get('correct_label', 0), results[label].get('label_count', 1)):<5.2f}%, "
            f"Correct label in top {top_n}: {get_percentage(results[label].get(f'top_{top_n}_label', 0), results[label].get('label_count', 1)):<5.2f}%, "
            f"Correct cat: {get_percentage(results[label].get('correct_label', 0), results[label].get('label_count', 1)):<5.2f}%, "
            f"Correct cat in top {top_n}: {get_percentage(results[label].get(f'top_{top_n}_category', 0), results[label].get('label_count', 1)):<5.2f}%, "
            f"Weighted cat: {round(results[label].get('weighted_category_score', 0), 2):<5.2f}, "
            f"Label count: {results[label].get('label_count', 0):<5.2f}"
            )

    logging.info(f"\nTotal results:\n{' '*4}"
        f"Total companies tested: {total_results.get('total_items', 0)}, after skipping {total_results.get('skipped', 0)} companies due to short text-data.\n{' '*4}"
        f"Correct label predictions: {get_percentage(total_results.get('correct_label', 0), total_results.get('total_items', 1))}%\n{' '*4}"
        f"Label in top {top_n} predictions: {get_percentage(total_results.get(f'top_{top_n}_label', 0), total_results.get('total_items', 1))}%\n{' '*4}"
        f"Correct category predictions: {get_percentage(total_results.get('correct_category', 0), total_results.get('total_items', 1))}%\n{' '*4}"
        f"Category in top {top_n} predictions: {get_percentage(total_results.get(f'top_{top_n}_category', 0), total_results.get('total_items', 1))}%\n{' '*4}"
        f"Weighted category score: {round(total_results.get('weighted_category_score', 0), 3)}{' '*4}")

def main(model_path: Annotated[Path, typer.Argument(..., dir_okay=True)] = "training/model-best",
        min_data_length: Annotated[int, typer.Argument()] = 300,
        evaluate_top_n: Annotated[int, typer.Argument()] = 5
    ):
    """
    Evaluate the model on the test set.
    
    :param model_path (Path): the path to the model
    :param min_data_length (int): the minimum length of the data to be evaluated
    :param evaluate_top_n (int): the number of top predictions to evaluate
    """
    logging.info("Starting evaluation")
    test_data, model = load_data_and_model(model_path)
    label_results = dict()
    
    for data_point in test_data:
        point_results = {'label': None, 'results': {}}
        text = str()
        """Combine all text data for the company into one string."""
        for data in data_point['data']:
            text += " " + data['data']
        if len(text) > 1000000: # SpaCy has a limit of 1000000 characters per document.
            text = text[:1000000]
            logging.debug(f"Text for company_id: {data_point['company_id']}, " 
                          f"Label: {data_point['branch_codes'][0]} is too long, cutting it to 1000000 characters")
        elif len(text) < min_data_length:
            logging.debug(f"Text for company_id: {data_point['company_id']}, "
                          f"Label: {data_point['branch_codes'][0]} is too short, skipping it") 
            point_results.update({'label': data_point['branch_codes'][0], 'results': {'skipped': 1}})
        else:
            point_results = evaluation(model(text).cats, data_point['branch_codes'][0], evaluate_top_n)
        label_results = update_label_results(label_results, point_results)

    log_results(label_results, evaluate_top_n)

if __name__ == '__main__':
    from aux_functions.logger_config import conf_logger
    conf_logger(Path(__file__).stem)
    typer.run(main)
