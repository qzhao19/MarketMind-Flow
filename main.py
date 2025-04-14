import uvicorn
from src.api.app import app

if __name__ == "__main__":
    uvicorn.run(
        # "src.api.app:app",
        app,
        host="0.0.0.0",
        port=8012,
        reload=True
    )