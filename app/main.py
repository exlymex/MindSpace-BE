from fastapi import FastAPI
from app.api.v1.endpoints import user  # Directly import the user module

app = FastAPI(title="MindSpace API")

# Include API routers
app.include_router(user.router, prefix="/api/v1")

# Optional: Add middleware (CORS, etc.) here
