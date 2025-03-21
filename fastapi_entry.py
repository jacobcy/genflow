from app import create_app
import os

app, fastapi_app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('FRONTEND_PORT', '6060'))
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
