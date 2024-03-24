import pandas as pd
from sklearn.preprocessing import OneHotEncoder

from app.classes import UserParams

bin_features = [
    "isComplete",
    "balcony",
    "passenger_elevator",
    "passenger_elevator",
    "is_apartments",
    "is_auction",
    "is_metro",
]
cat_features = ["region", "house_material", "locate", "m_type"]
num_features = [
    "total_area",
    "kitchen_area",
    "living_area",
    "rooms_count",
    "floor",
    "floors_number",
    "isComplete",
    "balcony",
    "passenger_elevator",
    "is_apartments",
    "is_auction",
    "is_metro",
    "m_minute",
]
required_columns = [
    "region_ekb",
    "region_kzn",
    "region_msk",
    "region_nng",
    "region_nsk",
    "region_spb",
    "house_material_block",
    "house_material_brick",
    "house_material_gasSilicateBlock",
    "house_material_monolith",
    "house_material_monolithBrick",
    "house_material_old",
    "house_material_panel",
    "house_material_stalin",
    "house_material_wood",
    "locate_Волга",
    "locate_Евро",
    "locate_Урал",
    "m_type_NO",
    "m_type_walk",
    "total_area",
    "kitchen_area",
    "living_area",
    "rooms_count",
    "floor",
    "floors_number",
    "isСomplete",
    "balcony",
    "passenger_elevator",
    "is_apartments",
    "is_auction",
    "is_metro",
    "m_minute",
]


def preprocess_user_input_main(X: UserParams):
    allowed_regions = {
        "Москва": "msk",
        "Санкт-Петербург": "spb",
        "Новосибирск": "nsk",
        "Екатеринбург": "ekb",
        "Нижний Новгород": "nng",
        "Казань": "kzn",
    }

    allowed_house_materials = {
        "Монолитный": "monolith",
        "Кирпичный": "brick",
        "Кирпично-монолитный": "monolithBrick",
        "Панельный": "panel",
        "Сталинский": "stalin",
        "Блочный": "block",
        "Старый": "old",
        "Деревянный": "wood",
        "Газосиликатный блок": "gasSilicateBlock",
    }

    X.region = allowed_regions[X.region]

    X.house_material = allowed_house_materials[X.house_material]

    if X.is_metro:
        X.m_type = "walk"
    else:
        X.m_type = "NO"
        X.m_minute = 0

    if X.region in ['msk', 'spb']:
        X.locate = 'Евро'
    elif X.region in ['ekb', 'nsk']:
        X.locate = 'Урал'
    else:
        X.locate = 'Волга'

    for feature in bin_features:
        if getattr(X, feature) is None:
            setattr(X, feature, 0)

    X = pd.DataFrame(X)
    X = X.transpose()
    X.columns = X.iloc[0, :]
    X = X.drop(index=0)

    for feature in bin_features:
        X[feature] = X[feature].astype("int")

    return X


def preprocess_user_input_lr(X: UserParams):
    X = preprocess_user_input_main(X)

    X_cat_features = X[cat_features]
    X_num_features = X[num_features]

    encoder = OneHotEncoder(sparse_output=False)
    encoder.fit(X_cat_features)

    X_encoded = pd.DataFrame(
        encoder.transform(X_cat_features),
        columns=encoder.get_feature_names_out(X_cat_features.columns),
    )
    X = pd.concat(
        [X_encoded.reset_index(drop=True), X_num_features.reset_index(drop=True)],
        axis=1,
    )

    for column in required_columns:
        if column not in X.columns:
            X[column] = 0.0

    X = X[required_columns]

    return X


def preprocess_user_input_catboost(X: UserParams):
    X = preprocess_user_input_main(X)

    return X


def preprocess_parse_data():
    df = pd.read_csv("csv/data.csv")

    df.loc[(df["region"] == "msk") | (df["region"] == "spb"), "locate"] = "Евро"
    df.loc[(df["region"] == "ekb") | (df["region"] == "nsk"), "locate"] = "Урал"
    df.loc[(df["region"] == "kzn") | (df["region"] == "nng"), "locate"] = "Волга"

    df.loc[df["living_area"].isna(), "living_area"] = df["total_area"] / 2
    df.loc[df["kitchen_area"].isna(), "kitchen_area"] = df["total_area"] * 0.2
    df = df[df["living_area"] < 150]
    df = df[df["kitchen_area"] < 150]
    df = df.reset_index(drop=True)

    df.loc[(df["total_area"] > 175) & (df["rooms_count"].isna()), "rooms_count"] = 4
    df.loc[(df["total_area"] > 125) & (df["rooms_count"].isna()), "rooms_count"] = 3
    df.loc[(df["total_area"] > 80) & (df["rooms_count"].isna()), "rooms_count"] = 2
    df.loc[(df["total_area"] < 40) & (df["rooms_count"].isna()), "rooms_count"] = 1

    coords_index = {}
    for i in range(df.shape[0]):
        coords_index[(df.loc[i, "latitude"], df.loc[i, "longitude"])] = i

    for i in range(df.shape[0]):
        defaults_index = coords_index.get(
            (df.loc[i, "latitude"], df.loc[i, "longitude"]), None
        )

        if defaults_index is None:
            continue

        for c in df.columns:
            if not pd.isnull(df.loc[i, c]) and pd.isnull(df.loc[defaults_index, c]):
                df.loc[i, c] = df.loc[defaults_index, c]

    df.loc[(df["floors_number"] > 20) & (df["build_date"].isna()), "build_date"] = 2010
    df.loc[df["build_date"].fillna(2025).astype(int) < 2024, "isComplete"] = 1
    df.loc[df["complitation_year"].fillna(2023).astype(int) > 2024, "isComplete"] = 0

    df["balcony"] = df["balcony"].fillna(0)
    df["is_apartments"] = df["is_apartments"].fillna(0)

    df.loc[
        (df["floors_number"] > 30) & (df["build_date"] > 2000) & (df["parking"].isna()),
        "parking",
    ] = "underground"

    for i in range(len(df)):
        if not pd.isnull(df.loc[i, "metro"]):
            df.loc[i, "is_metro"] = 1
        else:
            df.loc[i, "is_metro"] = 0

    for i in range(len(df)):
        if df.loc[i, "is_metro"] == 1:
            m_ls1 = list(map(lambda i: int(i), df.loc[2, "metro_distance"].split(",")))
            m_ls2 = df.loc[2, "metro_transport"].split(",")
            l = []
            for j in range(len(m_ls2)):
                if "walk" == m_ls2[j]:
                    l.append(j)
            if len(l) == 0:
                df.loc[i, "m_type"] = "transport"
                df.loc[i, "m_minute"] = min(m_ls1)
            else:
                d = 100
                for k in l:
                    if m_ls1[k] < d:
                        d = m_ls1[k]
                df.loc[i, "m_minute"] = d
                df.loc[i, "m_type"] = "walk"

    df.loc[
        (df["passenger_elevator"].isna()) & (~df["cargo_elevator"].isna()),
        "passenger_elevator",
    ] = 1
    df.loc[
        (df["passenger_elevator"].isna()) & (df["floors_number"] < 7),
        "passenger_elevator",
    ] = 1
    df["passenger_elevator"] = df["passenger_elevator"].fillna(0)
    df["isComplete"] = df["isComplete"].fillna(0)
    df["house_material"] = df["house_material"].fillna("monolithBrick")
    df = df.drop(
        [
            "metro",
            "metro_distance",
            "metro_transport",
            "decoration",
            "parking",
            "build_date",
            "complitation_year",
            "cargo_elevator",
        ],
        axis=1,
    )
    df = df[~df["rooms_count"].isna()]
    df = df[~df["district"].isna()]
    df["m_type"] = df["m_type"].fillna("NO")
    df["m_minute"] = df["m_minute"].fillna(0)
    df = df.drop(["address", "district", "longitude", "latitude"], axis=1)
    df["rooms_count"] = df["rooms_count"].astype(int)
    df["balcony"] = df["balcony"].astype(int)
    df["passenger_elevator"] = df["passenger_elevator"].astype(int)
    df["is_auction"] = df["is_auction"].astype(int)
    df["is_metro"] = df["is_metro"].astype(int)
    df["is_apartments"] = df["is_apartments"].astype(int)
    df["isСomplete"] = df["isСomplete"].astype(int)
    df["m_minute"] = df["m_minute"].astype(int)

    df.to_csv("csv/preprocessed_data.csv")


if __name__ == "__main__":
    features = UserParams(
        region='Москва',
        total_area=1,
        kitchen_area=1,
        living_area=1,
        rooms_count=1,
        floor=1,
        floors_number=1,
        isComplete=1,
        house_material='Кирпичный',
        balcony=1,
        passenger_elevator=1,
        is_apartments=1,
        is_auction=1,
        is_metro=0,
    )

    print(preprocess_user_input_catboost(features))

