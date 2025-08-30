from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from .config.database import (
    initialize_database_engine,
)
from .utils.my_logger import get_logger
from .config.my_settings import settings
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

# LIFESPAN
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    await startup_event(app)

    # This is where the app runs (yield)
    yield 

    # Shutdown event
    await shutdown_event(app)

# FASTAPI APP
app = FastAPI(
    version="0.1.0",
    lifespan=lifespan  
)

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# STARTUP EVENT
async def startup_event(app: FastAPI):
    get_logger(name="UZAIR").info("🚀 Starting up Data Migration Project...")
    
    # Initialize and store in app.state
    app.state.database_engine = initialize_database_engine()
    
    # Create database tables
    try:
        from sqlmodel import SQLModel
        from .models.user_model import UserSignUp
        from .models.youtube_token_model import GoogleToken
        from .models.video_model import Video
        from .models.gemini_key_model import GeminiKey
        from .models.dashboard_overview_model import DashboardOverview
        from .models.dashboard_playlist_model import DashboardPlaylist
        from .models.dashboard_video_model import DashboardVideo
        from .models.dashboard_playlist_video_model import DashboardPlaylistVideo
        from .models.youtube_credentials_model import YouTubeCredentials
        
        # Create all tables
        SQLModel.metadata.create_all(app.state.database_engine)
        get_logger(name="UZAIR").info("✅ Database tables created successfully")
    except Exception as e:
        get_logger(name="UZAIR").error(f"❌ Error creating database tables: {e}")

# INCLUDE ROUTERS
from .routes.auth_routes import router as auth_router
from .routes.youtube_token_controller import router as youtube_token_router
from .routes.video_routes import router as video_router
from .routes.title_generator_routes import router as title_generator_router
from .routes.time_stamps_generator_routes import router as time_stamps_generator_router
from .routes.description_generator_routes import router as description_generator_router
from .routes.thumbnail_generator_routes import router as thumbnail_generator_router
from .routes.gemini_key_routes import router as gemini_key_router
from .routes.playlist_routes import router as playlist_router
from .routes.privacy_status_routes import router as privacy_status_router
from .routes.schedule_routes import router as schedule_router
from .routes.youtube_upload_routes import router as youtube_upload_router
from .routes.dashboard_routes import router as dashboard_router
from .routes.youtube_credentials_routes import router as youtube_credentials_router

app.include_router(auth_router)
app.include_router(youtube_credentials_router)
app.include_router(youtube_token_router)
app.include_router(gemini_key_router)
app.include_router(video_router)
app.include_router(title_generator_router)
app.include_router(time_stamps_generator_router)
app.include_router(description_generator_router)
app.include_router(thumbnail_generator_router)
app.include_router(playlist_router)
app.include_router(privacy_status_router)
app.include_router(schedule_router)
app.include_router(youtube_upload_router)
app.include_router(dashboard_router)

# MOUNT STATIC FILES
from pathlib import Path

# Create thumbnails directory if it doesn't exist
thumbnails_dir = Path("thumbnails")
thumbnails_dir.mkdir(exist_ok=True)

# Mount static files directories
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/videos", StaticFiles(directory="videos"), name="videos")
app.mount("/thumbnails", StaticFiles(directory="thumbnails"), name="thumbnails")

# ROOT REDIRECT TO DOCS
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

# HEALTH CHECK
@app.get("/health")
async def health_check():
    return {"status": "The server is running successfully"}

# SHUTDOWN EVENT
async def shutdown_event(app: FastAPI):
    get_logger(name="UZAIR").info("🛑 Shutting down Data Migration Project...")
    
    # Cleanup - ClickHouse client doesn't need explicit closing
    # The client will be garbage collected automatically
    if hasattr(app.state, 'cartlow_clickhouse_prod_client'):
        get_logger(name="UZAIR").info("✅ ClickHouse client cleanup completed")
    if hasattr(app.state, 'cartlow_fantacy4_mysql_engine'):
        get_logger(name="UZAIR").info("✅ Cartlow Fantacy4 MySQL engine cleanup completed")
    if hasattr(app.state, 'cartlow_dev_mysql_engine'):
        get_logger(name="UZAIR").info("✅ Cartlow Dev MySQL engine cleanup completed")
    if hasattr(app.state, 'cartlow_prod_mysql_engine'):
        get_logger(name="UZAIR").info("✅ Cartlow Prod MySQL engine cleanup completed")