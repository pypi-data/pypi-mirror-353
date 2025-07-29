import json

from loguru import logger


def save_path(path):
    """
    Saves the WoW retail folder path to a configuration file.
    """
    try:
        with open("config.json", "r+", encoding="utf-8") as f:
            json.dump({"wow_path": path}, f, ensure_ascii=False, indent=4)
        logger.info("WoW retail folder path saved successfully.")
    except FileNotFoundError as e:
        logger.info(f"Configuration file not found: {e}. Creating File.")
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump({"wow_path": path}, f, ensure_ascii=False, indent=4)
    except OSError as e:
        logger.error(f"Error saving WoW path: {e}")


def load_path():
    """
    Loads the WoW retail folder path from a configuration file.
    Returns the path if found, otherwise returns an empty string.
    """
    try:
        with open("config.json", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("wow_path", "")
    except FileNotFoundError:
        logger.warning("Configuration file not found. Returning empty path.")
        return ""
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from config file: {e}")
        return ""
    except OSError as e:
        logger.error(f"Error reading WoW path: {e}")
        return ""


def load_timestamp() -> int:
    """
    Loads the last update timestamp from a configuration file.
    Returns the timestamp if found, otherwise returns an empty string.
    """
    try:
        with open("config.json", encoding="utf-8") as f:
            config = json.load(f)
            timestamp: int = config.get("last_update_timestamp", 0)
            if timestamp:
                return timestamp
            else:
                logger.warning("No last update timestamp found in config file.")
                return 0
    except FileNotFoundError:
        logger.warning("Configuration file not found. Returning empty timestamp.")
        return 0
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from config file: {e}")
        return 0
    except OSError as e:
        logger.error(f"Error reading last update timestamp: {e}")
        return 0


def save_timestamp(timestamp: int):
    """
    Saves the last update timestamp to a configuration file.
    """
    try:
        with open("config.json", "r+", encoding="utf-8") as f:
            config = json.load(f)
            config["last_update_timestamp"] = timestamp
            f.seek(0)
            json.dump(config, f, ensure_ascii=False, indent=4)
            f.truncate()
        logger.info("Last update timestamp saved successfully.")
    except FileNotFoundError as e:
        logger.info(f"Configuration file not found: {e}. Creating File.")
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump({"last_update_timestamp": timestamp}, f, ensure_ascii=False, indent=4)
    except OSError as e:
        logger.error(f"Error saving last update timestamp: {e}")
