from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"service": "monitor"}


@app.get("/status")
def status():
    return {"status": "ok"}