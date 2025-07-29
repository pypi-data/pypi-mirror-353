from loguru import logger
from slpp import slpp as lua  # Import SLPP


def convert_to_lua(data) -> str:
    logger.info("Converting data to Lua format using SLPP (Server > Character structure)...")
    if not data or not isinstance(data, list):
        logger.warning("No data provided or data is not a list. Returning empty ParseScoreDB table.")
        return "ParseScoreDB = {}\\n-- No data available or data format incorrect"

    processed_data_for_lua = {}
    for player_entry in data:
        if not isinstance(player_entry, dict):
            logger.warning(f"Skipping non-dictionary item in data list: {type(player_entry)}")
            continue

        player_name = str(player_entry.get("name", "UnknownPlayer"))
        # Use server_slug for the top-level key, assuming it's clean enough for a Lua key
        # If server_slug can contain problematic characters for unquoted keys,
        # SLPP will handle it by quoting, e.g. ["server-slug with spaces"]
        server_key = str(player_entry.get("server_slug", "UnknownServer"))

        if server_key not in processed_data_for_lua:
            processed_data_for_lua[server_key] = {}

        player_metrics = {}
        for metric_key, metric_value in player_entry.items():
            # Exclude keys used for structure or internal IDs from the innermost metrics table
            if str(metric_key) not in ["name", "server_slug", "id", "char_id", "player_id"]:
                player_metrics[str(metric_key)] = metric_value

        # Add the player's metrics under ServerKey -> PlayerName
        processed_data_for_lua[server_key][player_name] = player_metrics

    if not processed_data_for_lua:
        logger.warning("No valid player data to convert after processing. Returning empty ParseScoreDB table.")
        return "ParseScoreDB = {}\\n-- No valid player data"

    try:
        lua_table_string = lua.encode(processed_data_for_lua)
        final_lua_string = f"ParseScoreDB = {lua_table_string}"

        logger.info("Data conversion to Lua successful using SLPP (Server > Character structure).")
        return final_lua_string
    except Exception as e:
        logger.exception(f"Error during SLPP conversion: {e}")
        return "ParseScoreDB = {}\\n-- Error during Lua conversion"


# Example usage (for testing purposes, can be removed)
if __name__ == "__main__":
    sample_data = [
        {
            "name": "TestPlayer",
            "server_slug": "TestServer",
            "id": 123,
            "klass": "Warrior",
            "spec": "Fury",
            "dps": 15000.5,
            "hps": 5000.2,
            "rank": "Gold",
            "some_bool": True,
            "nothing": None,
        },
        {
            "name": "AnotherPlayer",
            "server_slug": "TestServer",
            "id": 124,
            "klass": "Mage",
            "spec": "Frost",
            "dps": 22000.0,
        },
        {
            "name": "SoloPlayer",
            "server_slug": "OtherServer",
            "id": 125,
            "klass": "Hunter",
            "spec": "Beast Mastery",
            "dps": 18000.0,
        },
    ]
    lua_output = convert_to_lua(sample_data)
    print("--- Sample Data Test (Server > Character) ---")
    print(lua_output)
    # Expected output structure:
    # ParseScoreDB = {
    #   ["TestServer"] = {
    #     ["TestPlayer"] = { ["klass"] = "Warrior", ["spec"] = "Fury", ["dps"] = 15000.5, ... },
    #     ["AnotherPlayer"] = { ["klass"] = "Mage", ["spec"] = "Frost", ["dps"] = 22000.0, ... }
    #   },
    #   ["OtherServer"] = {
    #     ["SoloPlayer"] = { ["klass"] = "Hunter", ["spec"] = "Beast Mastery", ["dps"] = 18000.0, ... }
    #   }
    # }

    empty_data_output = convert_to_lua([])
    print("\\n--- Empty Data Test ---")
    print(empty_data_output)

    invalid_data_output = convert_to_lua(None)  # type: ignore
    print("\\n--- Invalid Data Test ---")
    print(invalid_data_output)

    single_player_no_metrics_to_exclude = [{"name": "Solo", "server_slug": "Alone", "id": 1}]
    print("\\n--- Single Player No Metrics (after exclusion) Test ---")
    # This should result in: { ["Alone"] = { ["Solo"] = {} } }
    print(convert_to_lua(single_player_no_metrics_to_exclude))
