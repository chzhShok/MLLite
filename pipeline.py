from ml.model import model_catboost
from ml.preprocess import preprocess_parse_data
from ml.parser import create_table


def main():
    create_table()
    preprocess_parse_data()
    model_catboost()
