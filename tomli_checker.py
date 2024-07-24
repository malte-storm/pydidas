import tomli
import logging
from typing import Optional, Dict, Any

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_toml_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load a TOML file and return its contents as a dictionary.

    Args:
        filepath (str): The path to the TOML file to be loaded.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the TOML content if successful, 
                                   or None if an error occurred.
    """
    try:
        with open(filepath, "rb") as f:
            toml_dict = tomli.load(f)
        logging.info("Successfully loaded TOML content.")
        logging.debug(f"TOML content: {toml_dict}")
        return toml_dict
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return None
    except tomli.TOMLDecodeError as e:
        logging.error(f"Error decoding TOML file '{filepath}': {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading '{filepath}': {e}")
        return None

if __name__ == "__main__":
    print("Starting script...")
    load_toml_file("./pyproject.toml")
