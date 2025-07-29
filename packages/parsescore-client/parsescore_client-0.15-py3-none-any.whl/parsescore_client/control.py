from time import sleep

import httpx
from loguru import logger

from .config import load_path, load_timestamp, save_timestamp
from .lua_converter import convert_to_lua

logger.add("../logs/client.log", rotation="10 MB", retention="7 days", level="INFO")

# --- Configuration ---
SERVER_URL = "http://194.164.192.122:13377"
ADDON_DIR = load_path() + "/Interface/AddOns/ParseScore/ParseScoreDB.lua"

# --- Core Client Logic ---


def check_for_updates() -> dict:
    """Checks with the server if new data is available."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{SERVER_URL}/check-update/?timestamp={load_timestamp()}")
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
    except httpx.RequestError as e:
        logger.exception(f"Error checking for updates: {e}")
        return {"update_available": False, "error": str(e)}
    except Exception as e:
        logger.exception(f"An unexpected error occurred while checking for updates: {e}")
        return {"update_available": False, "error": "An unexpected error occurred."}


def get_data_from_server():
    """Fetches the full dataset from the server."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{SERVER_URL}/get-data")
            response.raise_for_status()
            return response.json()  # Assuming server returns the data in a processable format
    except httpx.RequestError as e:
        logger.error(f"Error fetching data: {e}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred while fetching data. {e}")
        return None


def save_lua_file(lua_data):
    """Saves the Lua data to the specified addon directory."""
    try:
        # Ensure the directory exists (though for a file, os.makedirs is not strictly needed unless path is deep)
        # os.makedirs(os.path.dirname(ADDON_DIR), exist_ok=True) # Not needed if ADDON_DIR is a file path
        with open(ADDON_DIR, "w", encoding="utf-8") as f:
            f.write(lua_data)
        logger.info(f"Lua data saved to {ADDON_DIR}")
        return True
    except OSError as e:
        logger.error(f"Error saving Lua file: {e}")
        return False
    except Exception:
        logger.exception("An unexpected error occurred while saving the Lua file.")
        return False


def update_background():
    while True:
        update_info = check_for_updates()
        if update_info.get("update_available"):
            logger.info(f"Update available: {update_info['last_update_timestamp']}")
            data = get_data_from_server()
            if data:
                lua_data = convert_to_lua(data.get("data"))
                if save_lua_file(lua_data):
                    logger.info("Addon updated successfully.")
                    save_timestamp(int(update_info["last_update_timestamp"]))
                else:
                    logger.error("Failed to save the Lua file.")
        else:
            logger.info("No updates available.")

        sleep(60 * 15)
