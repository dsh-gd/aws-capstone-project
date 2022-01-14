import json


def save_data(data: list, filepath: str) -> None:
    """Save the dataset to a specific location.

    Args:
        data (list): A list to save.
        filepath (str): Location to save the list to as a JSON file.
    """
    with open(filepath, "w") as fp:
        json.dump(data, indent=2, fp=fp)


def load_data(filepath: str) -> list:
    """Load a list from a JSON's filepath.

    Args:
        filepath (str): JSON's filepath.

    Returns:
        A list with the data loaded.
    """
    with open(filepath) as fp:
        data = json.load(fp)
    return data
