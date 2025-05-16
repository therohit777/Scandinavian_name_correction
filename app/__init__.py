from fastapi import FastAPI
from app.log_config import LOGGING_CONFIG
import logging.config
from fastapi.middleware.cors import CORSMiddleware

# Initialize logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)  # get a logger instance

# Create FastAPI app with OpenAPI documentation configuration
app = FastAPI(
    title="Test-v1",
    description="""API for demo test !
    
    # Test cases
    test_cases = [
        ("Ake", "sweden"),      # Should be Åke
        ("Naeik", "sweden"),    # Should be Näik
        ("Gosta", "sweden"),    # Should be Gösta
        ("Soeren", "denmark"),  # Should be Søren
        ("Haakon", "norway"),   # Should be Håkon
        ("Oskar", "iceland"),   # Should be Óskar
        ("Tord", "iceland"),    # Should be Þord
        ("Aesa", "iceland"),    # Should be Æsa
        ("Moose", "denmark"),   # Should be Møse
    ]
    
    """,
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

from app.routes import router
app.include_router(router)