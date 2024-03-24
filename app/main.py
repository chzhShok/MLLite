from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
import joblib
from app.classes import UserParams
from ml.model import predict_lr, predict_catboost

MODEL_NAME = "model_catboost.pkl"

app = FastAPI(title="ML model")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

with open(f"{MODEL_NAME}", "rb") as file:
    model = joblib.load(file)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/result", response_class=HTMLResponse)
async def print_result(
        request: Request,
        region: str = Form(...),
        total_area: float = Form(...),
        kitchen_area: float = Form(...),
        living_area: float = Form(...),
        rooms_count: int = Form(...),
        floor: int = Form(...),
        floors_number: int = Form(...),
        isComplete: bool | None = Form(None),
        house_material: str = Form(...),
        balcony: bool | None = Form(None),
        passenger_elevator: bool | None = Form(None),
        is_auction: bool | None = Form(None),
        is_apartments: bool | None = Form(None),
        is_metro: bool | None = Form(None),
        m_minute: float | None = Form(None),
):
    params = UserParams(
        region=region,
        total_area=total_area,
        kitchen_area=kitchen_area,
        living_area=living_area,
        rooms_count=rooms_count,
        floor=floor,
        floors_number=floors_number,
        isComplete=isComplete,
        house_material=house_material,
        balcony=balcony,
        passenger_elevator=passenger_elevator,
        is_apartments=is_apartments,
        is_auction=is_auction,
        is_metro=is_metro,
        m_minute=m_minute,
    )

    predict = predict_catboost(params, model)[0]
    predict = f'{round(predict):,}'
    predict = predict.replace(',', ' ')

    return templates.TemplateResponse("result.html", {"request": request, "result": predict})
