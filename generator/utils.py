# generator/utils.py
# Utility functions.

import datetime
import json
import random
import re
from argparse import Namespace
from pathlib import Path

import boto3


def load_data(filepath: str) -> dict:
    """Load a dictionary from a JSON's filepath.
    Args:
        filepath (str): JSON's filepath.
    Returns:
        A dictionary with the data loaded.
    """
    with open(filepath) as fp:
        data = json.load(fp)
    return data


def dt_path(prefix: str, dt: datetime.datetime = None) -> str:
    """Create path for the file using date and time.

    Args:
        prefix (str): A prefix for the path.
        dt (datetime.datetime, optional): Date and time.

    Returns:
        The path to the file without extension.
        prefix/year/month/day/hour/timestamp
    """
    if not dt:
        dt = datetime.datetime.now()
    dt_str = dt.strftime("%Y/%m/%d/%H")
    attempt_id = dt.strftime("%Y%m%d%H%M%S")
    path = Path(prefix, dt_str, attempt_id)
    return str(path)


def latest_path(
    aws_config: Namespace,
    dset_prefix: str,
    dset_type: str = "",
    last_dt: datetime.datetime = None,
) -> str:
    """Get path of the latest dataset on S3.

    Args:
        aws_config (Namespace): AWS credentials and name of the bucket.
        dset_prefix (str): A prefix of the path to the dataset.
        dset_type (str, optional): Data set file type. (e.g "_available", "_unavailable")
        last_dt (datetime.datetime, optional): Date and time after which you do not need to search.

    Returns:
        Base path of the latest dataset.
    """
    s3 = boto3.resource(
        "s3",
        region_name=aws_config.region_name,
        aws_access_key_id=aws_config.aws_access_key_id,
        aws_secret_access_key=aws_config.aws_secret_access_key,
    )
    bucket = s3.Bucket(aws_config.bucket_name)

    objects = bucket.objects.filter(Prefix=dset_prefix)
    paths = [
        obj.key for obj in objects if obj.key.endswith(f"{dset_type}.json")
    ]

    if not paths:
        return None

    last_path = dt_path(dset_prefix, last_dt) if last_dt else None
    raw_path = None
    if not last_path:
        raw_path = paths[-1]
    else:
        for p in reversed(paths):
            if p < last_path:
                raw_path = p
                break

    if not raw_path:
        return None

    r = re.match(r"(.+/\d+)(_available|_unavailable)?.json", raw_path)
    path = r.groups()[0]
    return path


def save_data_s3(aws_config: Namespace, data: list, path: str) -> None:
    """Save data to a bucket on S3.

    Args:
        aws_config (Namespace): AWS credentials and name of the bucket.
        data (list): A list (or dictionary) to save.
        path (str): Path to the file.
    """
    s3 = boto3.resource(
        "s3",
        region_name=aws_config.region_name,
        aws_access_key_id=aws_config.aws_access_key_id,
        aws_secret_access_key=aws_config.aws_secret_access_key,
    )
    obj = s3.Object(aws_config.bucket_name, path)
    obj.put(
        Body=(bytes(json.dumps(data).encode("UTF-8"))),
        ContentType="application/json",
    )


def load_data_s3(aws_config: Namespace, path: str) -> list:
    """Load data from the bucket on S3.

    Args:
        aws_config (Namespace): AWS credentials and name of the bucket.
        path (str): Path to the file.

    Returns:
        A list with the data loaded.
    """
    s3 = boto3.resource(
        "s3",
        region_name=aws_config.region_name,
        aws_access_key_id=aws_config.aws_access_key_id,
        aws_secret_access_key=aws_config.aws_secret_access_key,
    )
    obj = s3.Object(aws_config.bucket_name, path)
    file_content = obj.get()["Body"].read().decode("utf-8")
    data = json.loads(file_content)
    return data


def to_delete(elements: list, n_del: int) -> set:
    """Return set with elements to delete.

    Args:
        elements (list): List with elements.
        n_del (int): Number of elements to delete.

    Returns:
        Set with elements to delete.
    """
    n = len(elements)
    if n_del > n:
        del_idxs = []
    else:
        del_idxs = random.sample(range(len(elements)), n_del)
    to_del = {elem for idx, elem in enumerate(elements) if idx in del_idxs}
    return to_del
