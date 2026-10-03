import uvicorn
from fastapi import FastAPI
from eyes_backend.routes import scraping_router, scan_router
from eyes_backend.settings import get_settings

app = FastAPI(
    title=get_settings().name,
    debug=get_settings().debug,
    version=get_settings().version
    
)
app.include_router(scraping_router)
app.include_router(scan_router)

def main():
    uvicorn.run(
        "eyes_backend.main:app",
        host=get_settings().host,
        port=get_settings().port,
        reload=True
    )