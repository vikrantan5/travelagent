"""
Server entry point for uvicorn
Imports the FastAPI app from api.app
"""


# Load environment variables first
from dotenv import load_dotenv
load_dotenv()


from api.app import app

# This allows uvicorn to find the app with: uvicorn server:app
__all__ = ['app']
