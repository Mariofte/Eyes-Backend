from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Eyes backend is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}