import joblib
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error, make_scorer
from sklearn.model_selection import GridSearchCV

from ml.preprocess import preprocess_user_input_lr, preprocess_user_input_catboost


def model_catboost():
    df = pd.read_csv("csv/preprocessed_data.csv")

    y = df["price"]
    X = df.drop(columns="price")

    # ftwo_scorer = make_scorer(mean_squared_error, beta=2)
    #
    # param_dict = [{'learning_rate': [0.01, 0.05, 0.025],
    #                'random_state': [42],
    #                'max_bin': [50, 100],
    #                'depth': [6, 10, 12],
    #                'loss_function': ['RMSE'],
    #                'eval_metric': ['RMSE'],
    #                'iterations': [500, 1000],
    #                'verbose': [False]}]
    #
    # model = CatBoostRegressor()
    # grid_cb = GridSearchCV(model, param_dict, cv=3, scoring=ftwo_scorer, n_jobs=-1)
    # grid_cb.fit(X, y, cat_features=['region', 'house_material', 'locate', 'm_type'])

    model = CatBoostRegressor(
        iterations=1500,
        depth=12,
        learning_rate=0.025,
        random_state=42,
        verbose=False,
        loss_function="RMSE",
        cat_features=["region", "house_material", "locate", "m_type"],
    )

    model.fit(X, y)

    filename = "model_catboost.pkl"

    joblib.dump(model, filename)


def predict_lr(params, model):
    preprocessed_data = preprocess_user_input_lr(params)

    predict = model.predict(list(preprocessed_data.values))

    return predict

def predict_catboost(params, model):
    preprocessed_data = preprocess_user_input_catboost(params)

    predict = model.predict(preprocessed_data)

    return predict