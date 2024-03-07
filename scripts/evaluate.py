import typer
import logging
import json
import spacy
from pathlib import Path
from typing_extensions import Annotated
from scripts.scb import SCBinterface

def evaluation(predictions: dict, true_label: str):
    """
    Evaluate the model predictions against the true label.
    """
    
    true_label_score = 0
    correct_category_score = 0
    
    sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
    
    for i, (label, score) in enumerate(sorted_predictions):
        if label == true_label:
            true_label_score = score
        if label[:2] == true_label[:2]:
            # Weight the score by the position in the list.
            true_label_score += score * (1/(i+1))
    return true_label_score, correct_category_score

def main(model_path: Annotated[Path, typer.Argument(..., dir_okay=True)] = "training/model-best"):
    logging.info("Starting evaluation")
    
    scb = SCBinterface()
    test_data = scb.fetch_test_set()
    
    nlp = spacy.load(model_path)

    total_true_label_score = 0
    total_correct_category_score = 0
    for company in test_data:
        text = ""
        for data_point in company['data']:
            text += " " + data_point['data']
        if len(text) > 1000000:
            text = text[:1000000]
        true_label_score, correct_category_score = evaluation( nlp(text).cats, company['branch_codes'][0])
        total_true_label_score += true_label_score
        total_correct_category_score += correct_category_score
    
    final_true_label_score = total_true_label_score / len(test_data)
    final_correct_category_score = total_correct_category_score / len(test_data)

    
    print(f"True label score: {final_true_label_score}")
    print(f"Correct category score: {final_correct_category_score}")
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    typer.run(main)