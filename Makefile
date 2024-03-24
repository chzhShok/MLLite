dev:
	uvicorn --reload app.main:app

prod:
	uvicorn --host 0.0.0.0 app.main:app