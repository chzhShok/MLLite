import os
import csv
import requests
import cfscrape
import traceback
from tqdm import tqdm
from time import sleep

PAUSE_TIME = 5  # Увеличиваем интервалы отправки запросов — борьба с капчей
# CSV_NUMBER = datetime.now().strftime("%d-%m-%Y")  # Постфикс названия создаваемой таблицы
CSV_PATH = os.path.normpath(
    os.path.join(os.getcwd(), "ml/csv")
)  # Создаём папку 'csv' для записи создаваемых таблиц
if not os.path.exists(CSV_PATH):  # ...если такой не существовало ранее
    os.mkdir(CSV_PATH)
    print(f"Folder {CSV_PATH} has been created!")

# Словарь некоторых городов с номерами, объявления по которым можно искать на Циан
regions = {
    "msk": 1,  # Москва
    "spb": 2,  # Санкт–Петербург
    "ekb": 4743,  # Екатеринбург
    "nsk": 4897,  # Новосибирск
    "kzn": 4777,  # Казань
    "nng": 4885,  # Нижний Новгород
}

# Названия столбцов (header) будущей таблицы,
# которые связываются с отобранными признаками в create_table()
dataset = [
    [
        "region",
        "address",
        "price",
        "total_area",
        "kitchen_area",
        "living_area",
        "rooms_count",
        "floor",
        "floors_number",
        "build_date",
        "isComplete",
        "complitation_year",
        "house_material",
        "parking",
        "decoration",
        "balcony",
        "longitude",
        "latitude",
        "passenger_elevator",
        "cargo_elevator",
        "metro",
        "metro_distance",
        "metro_transport",
        "district",
        "is_apartments",
        "is_auction",
    ]
]


# Функция для обработки пропусков и булевых значений
def add_attr(attr):
    if isinstance(attr, bool):
        return int(attr)

    return attr if attr is not None else "empty"


# Функция для создания экземпляра класса запросов
def get_session():
    # Передаваемые параметры для экземпляра (как получить — туториал ниже)

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://www.cian.ru",
        "Cookie": '_dc_gtm_UA-30374201-1=1; _ga=GA1.2.883619009.1710865976; _gid=GA1.2.978674106.1710865976; __cf_bm=ukN1c4sFNYuMKN9ukpBuzjqD1ZBG19zEsswBnndEqhM-1710937848-1.0.1.1-zzKDqrdrVtB_t3vcg4.bxn1tckTY.yhFZdQZYbO65xwFSeIz31Zg8h2NVVPdbpfVARzxaaQoQ.7dfuuND36kUw; _ga_3369S417EL=GS1.1.1710870227.3.0.1710870227.60.0.0; _gpVisits={"isFirstVisitDomain":true,"idContainer":"1000252B"}; afUserId=56fff16e-827f-411a-a8eb-df93df3ba6ed-p; tmr_lvid=3ce81288134c5bf64dba6f90c207bb4e; tmr_lvidTS=1710865974429; _gcl_au=1.1.396553595.1710865974; session_main_town_region_id=1; session_region_id=1; AF_SYNC=1710865978066; _ym_isad=2; adrcid=ANwtW43LvzM4Ddam_jKJIdw; _ym_d=1710865977; _ym_uid=1710865977350230654; cookie_agreement_accepted=1; login_mro_popup=1; sopr_utm=%7B%22utm_source%22%3A+%22direct%22%2C+%22utm_medium%22%3A+%22None%22%7D; uxs_uid=56fb1450-e60e-11ee-89e7-eb9afd486469; _CIAN_GK=008dde10-0b06-48f3-8f25-bdf07d33e0d6',
        "Content-Length": "217",
        "Accept-Language": "ru",
        "Host": "api.cian.ru",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Referer": "https://www.cian.ru/",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    session = requests.Session()
    session.headers = headers
    return cfscrape.create_scraper(
        sess=session
    )  # cfscrape — обход защиты от ботов Cloudflare


# Записываем всё в файл формата .csv
def recording_table():
    try:
        with open(
            os.path.join(CSV_PATH, f"data.csv"), mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            for row in dataset:
                writer.writerow(row)

        print(f'The dataset is written in file "data.csv"')
        return

    except Exception as error:
        print("Recording error!\n", traceback.format_exc())
        sleep(PAUSE_TIME)
        return


# Получаем формат json (питоновский dict) из нашего запроса Response
def get_json(session, region_name, cur_page):
    # Параметры, которые отображаются в URL-запросе
    # https://www.cian.ru/cat.php/?deal_type=sale&engine_version=2&offer_type=flat&region=1&
    # room1=1&room2=1&room3=1&room4=1&room5=1&room6=1
    json_data = {
        "jsonQuery": {
            "_type": "flatsale",
            "engine_version": {
                "type": "term",
                "value": 2,
            },
            "region": {
                "type": "terms",
                "value": [
                    regions[region_name],
                ],
            },
            "room": {
                "type": "terms",
                "value": [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                ],
            },
            "page": {
                "type": "term",
                "value": cur_page,
            },
            # Можно задавать дополнительные атрибуты фильтрации объявлений
            # 'price': {
            #     'type': 'range',
            #     'value': {
            #         'gte': min_price,
            #         'lte': max_price,
            #     },
            # },
        },
    }

    # Получаем запрос с заданными параметрами
    # Возвращаемое значение — bytes
    try:
        response = session.post(
            "https://api.cian.ru/search-offers/v2/search-offers-desktop/",
            json=json_data,
        )

    except:
        return f"oops! Error {response.status_code}"

    # Получаем формат .json
    if response.status_code != 204 and response.headers[
        "content-type"
    ].strip().startswith("application/json"):
        try:
            return response.json()
        except ValueError:
            return f"oops! ValueError!"


def create_table(region_name="msk", start_page=1, end_page=55, number_of_samples=100):
    # В Циан выдаются страницы в диапазоне [1, 54]
    if start_page < 1:
        start_page = 1
    if end_page > 55:
        end_page = 55

    session = get_session()

    cnt_samples = 0
    for cur_page in tqdm(
        range(start_page, end_page)
    ):  # tqdm — выводим прогресс выполнения цикла
        if cnt_samples >= number_of_samples:
            break

        data = get_json(session, region_name, cur_page)
        if data is None:
            print("oops! Captcha!")
            return
        if isinstance(data, str):
            print(data)
            continue

        # Отбираем из большого словаря то, что нам нужно (можно и больше — смотри data)
        for item in data["data"]["offersSerialized"]:
            cur_item = [
                region_name,
                add_attr(item["geo"]["userInput"]),
                add_attr(item["bargainTerms"]["priceRur"]),
                add_attr(item.get("totalArea")),
                add_attr(item.get("kitchenArea")),
                add_attr(item.get("livingArea")),
                add_attr(item.get("roomsCount")),
                add_attr(item.get("floorNumber")),
                add_attr(item["building"].get("floorsCount")),
                add_attr(item["building"].get("buildYear")),
                add_attr(
                    item["building"]["deadline"]["isComplete"]
                    if item["building"].get("deadline") is not None
                    else None
                ),
                add_attr(
                    item["building"]["deadline"]["year"]
                    if item["building"].get("deadline") is not None
                    else None
                ),
                add_attr(item["building"].get("materialType")),
                add_attr(
                    item["building"]["parking"]["type"]
                    if item["building"].get("parking") is not None
                    else None
                ),
                add_attr(item.get("decoration")),
                add_attr(item.get("balconiesCount")),
                add_attr(item["geo"]["coordinates"]["lng"]),
                add_attr(item["geo"]["coordinates"]["lat"]),
                add_attr(item["building"].get("passengerLiftsCount")),
                add_attr(item["building"].get("cargoLiftsCount")),
                add_attr(
                    ",".join(
                        [
                            str(x["name"])
                            for x in item["geo"]["undergrounds"]
                            if x is not None
                        ]
                    )
                ),
                add_attr(
                    ",".join(
                        [
                            str(x["time"])
                            for x in item["geo"]["undergrounds"]
                            if x is not None
                        ]
                    )
                ),
                add_attr(
                    ",".join(
                        [
                            str(x["transportType"])
                            for x in item["geo"]["undergrounds"]
                            if x is not None
                        ]
                    )
                ),
                add_attr(
                    ",".join(
                        [
                            str(x["name"])
                            for x in item["geo"]["districts"]
                            if x is not None
                        ]
                    )
                ),
                add_attr(item.get("isApartments")),
                add_attr(item.get("isAuction")),
            ]

            if cur_item not in dataset:
                dataset.append(cur_item)
                cnt_samples += 1
            else:
                continue

            if cnt_samples >= number_of_samples:
                break

        print(f"{cnt_samples} / {number_of_samples} | page: {cur_page}")
        sleep(PAUSE_TIME)

    recording_table()
