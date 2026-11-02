import uvicorn
from eyes_backend.log_config import get_log_config
from eyes_backend.settings import get_settings

def main():
    settings = get_settings()
    # main.py
    uvicorn.run(
        "eyes_backend.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=get_log_config(debug=settings.debug),
        access_log=False,  # evita líneas duplicadas
    )