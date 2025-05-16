import datetime
import logging

import pytz
from app.controller import correct_scandinavian_name
from app.models import ApiResponse, UserData
from fastapi import APIRouter

# Configure logger
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/server-check")
def health_check():
    try:
        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Server check endpoint hit at {current_time}")

        return ApiResponse(
            status_code=200,
            message="Server check successful. Welcome to Test-v1 Server!",
            data={
                "serverName": "Test-v1",
                "timestamp": current_time
            }
        )

    except Exception as e:
        print(e)
        logger.error(f"An ERROR occurred in the Server check: {e}")
        return ApiResponse(
            status_code=500,
            message="Server check failed.",
            data={}
        )


@router.post("/name_correction")
async def create_conversation(user_data: UserData):
    """
    Create a new conversation
    Takes a user's email and creates a new conversation with a unique ID.
    """
    logger.info("Name Correction endpoint accessed !")
    response = await correct_scandinavian_name(user_data.user_name,user_data.country)
    logger.info(f"API logs fetched successfully. Response: {response}")
    return response