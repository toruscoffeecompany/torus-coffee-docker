import os
from pathlib import Path
from dotenv import load_dotenv
from app.main import create_app

load_dotenv()

app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
