from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"service": "analyzer"}


@app.get("/analyze")
def analyze():
    return {"status": "analyzing data"}