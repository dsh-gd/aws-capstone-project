# generator/utils.py
# Utility functions.

import datetime
import json
from argparse import Namespace
from pathlib import Path

import boto3


def save_data(data: list, filepath: str) -> None:
    """Save data to a specific location.

    Args:
        data (list): A list (or dictionary) to save.
        filepath (str): Location to save the list (or dictionary) to as a JSON file.
    """
    with open(filepath, "w") as fp:
        json.dump(data, indent=2, fp=fp)


def load_data(filepath: str) -> list:
    """Load a list (or dictionary) from a JSON's filepath.

    Args:
        filepath (str): JSON's filepath.

    Returns:
        A list (or dictionary) with the data loaded.
    """
    with open(filepath) as fp:
        data = json.load(fp)
    return data


def dt_path(prefix: str, ext: str = ".json") -> str:
    """Create the path of the file using the date and time.

    Args:
        prefix (str): A prefix for the path.
        ext (str): An extension of the file. (Default is ".json")

    Returns:
        The path to the file.

    Example:
        item/2022/01/20/13.json
    """
    now = datetime.datetime.now()
    date = now.strftime("%Y/%m/%d")
    fname = f"{now.hour}{ext}"
    path = Path(prefix, date, fname)
    return str(path)


def save_data_s3(aws_config: Namespace, data: list, dprefix: str) -> None:
    """Save data to a bucket on S3.

    Args:
        aws_config (Namespace): AWS credentials and name of the bucket.
        data (list): A list (or dictionary) to save.
        dprefix (str): A prefix for the dataset path.
    """
    s3 = boto3.resource(
        "s3",
        region_name=aws_config.region_name,
        aws_access_key_id=aws_config.aws_access_key_id,
        aws_secret_access_key=aws_config.aws_secret_access_key,
    )
    path = dt_path(dprefix)
    s3_obj = s3.Object(aws_config.bucket_name, path)
    s3_obj.put(
        Body=(bytes(json.dumps(data).encode("UTF-8"))),
        ContentType="application/json",
    )


def collect_values_s3(
    aws_config: Namespace, dprefix: str, key: str = None
) -> list:
    """Collect data values from the dataset.

    Args:
        aws_config (Namespace): AWS credentials and name of the bucket.
        dprefix (str): A prefix for the dataset path.
        key (str, optional): A key for collecting values from the dictionaries.

    Returns:
        A list with the data values.
    """
    s3 = boto3.resource(
        "s3",
        region_name=aws_config.region_name,
        aws_access_key_id=aws_config.aws_access_key_id,
        aws_secret_access_key=aws_config.aws_secret_access_key,
    )
    bucket = s3.Bucket(aws_config.bucket_name)

    values = []
    for obj in bucket.objects.filter(Prefix=dprefix):
        data = json.load(obj.get()["Body"])
        if key:
            values.extend([o[key] for o in data])
        else:
            values.extend(data)

    return values
