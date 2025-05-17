from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import uvicorn
from sqlalchemy.orm import Session

from app.config import settings, UPLOAD_DIRECTORY
from app.database import engine, Base, get_db
from app.models import user, journal, notification
from app.routers import auth, journals, users, graphql
from app.services.auth import get_current_user

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="School Journal API",
    description="API for managing school journals and student notifications",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routers with prefix
app.include_router(
    auth.router,
    prefix=f"{settings.API_PREFIX}/auth",
    tags=["Authentication"]
)
app.include_router(
    users.router,
    prefix=f"{settings.API_PREFIX}/users",
    tags=["Users"]
)
app.include_router(
    journals.router,
    prefix=f"{settings.API_PREFIX}/journals",
    tags=["Journals"]
)

# Include GraphQL router if enabled
if settings.enable_graphql:
    app.include_router(
        graphql.router,
        prefix=f"{settings.API_PREFIX}/graphql",
        tags=["GraphQL"]
    )

# Root endpoint - serve the SPA
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("app/static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Authentication status endpoint
@app.get(f"{settings.API_PREFIX}/auth/status")
async def auth_status(current_user = Depends(get_current_user)):
    """Check authentication status and return user info."""
    return {
        "authenticated": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "user_type": current_user.user_type,
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "detail": exc.detail,
        "status_code": exc.status_code
    }

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if settings.debug:
        print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# Run the application if executed directly
if __name__ == "__main__":
    # Use uvicorn to run the app with settings from config
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )