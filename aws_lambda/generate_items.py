import json
from argparse import Namespace

import data
import utils

params_fp = "/opt/generator_params.json"


def items_dset(
    params: Namespace, size: int = 1000, n_del: int = 5, dt: str = None
):
    try:
        items = data.generate_items(params, size)
    except AttributeError:
        return 400, "Some parameters are incorrect or missing."
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Data wasn't generated."

    dset_prefix = "items"
    try:
        base_path = utils.dt_path(dset_prefix, dt)
        utils.save_data_s3(items, base_path + ".json")
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Data wasn't saved to S3."

    base_lst_path = utils.latest_path(dset_prefix, "_available", dt)
    if base_lst_path:
        try:
            available = utils.load_data_s3(base_lst_path + "_available.json")
        except:  # NOQA: E722 (do not use bare 'except')
            return 500, "Can't load available items from S3."
    else:
        available = []

    new_available = available + [item["id"] for item in items]
    try:
        utils.save_data_s3(new_available, base_path + "_available.json")
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Data wasn't saved to S3."

    return 200, f"{size} items generated."


def lambda_handler(event, context):
    if not event["body"]:
        status_code, msg = 400, "Parameters not provided."
    else:
        body = json.loads(event["body"])
        size = body.get("size", 100)
        n_del = body.get("n_del", 5)
        dt = body.get("dt", None)
        if "params" in body:
            params = Namespace(**body["params"])
        else:
            params = Namespace(**utils.load_data(filepath=params_fp))
        status_code, msg = items_dset(params, size, n_del, dt)
    return {"statusCode": status_code, "body": json.dumps(msg)}
