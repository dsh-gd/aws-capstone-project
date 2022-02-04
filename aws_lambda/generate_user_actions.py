import json
from argparse import Namespace
from datetime import datetime, timedelta

import boto3
import data
import utils

params_fp = "/opt/generator_params.json"

lambda_client = boto3.client("lambda")


def user_actions_dset(params: Namespace, size: int = 1000):
    try:
        user_ids_path = utils.latest_path("user_ids") + ".json"
        user_ids = utils.load_data_s3(path=user_ids_path)
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Cannot load user IDs from S3."

    try:
        base_items_path = utils.latest_path(
            dset_prefix="items", dset_type="_available"
        )
        items_path = base_items_path + "_available.json"
        items_ids = utils.load_data_s3(path=items_path)
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Cannot load items from S3."

    try:
        user_actions = data.generate_user_actions(
            params, user_ids, items_ids, size
        )
    except AttributeError:
        return 400, "Some parameters are incorrect or missing."
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Data wasn't generated."

    try:
        path = utils.dt_path("user_actions") + ".json"
        utils.save_data_s3(data=user_actions, path=path)
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Data wasn't saved to S3."

    return 200, f"{len(user_actions)} user actions generated."


def lambda_handler(event, context):
    if not event["body"]:
        status_code, msg = 400, "Parameters not provided."
    else:
        body = json.loads(event["body"])
        size = body.get("size", 10000)
        if "params" in body:
            params = Namespace(**body["params"])
        else:
            params = Namespace(**utils.load_data(filepath=params_fp))

        start_date = body.get("start_date", None)
        end_date = body.get("end_date", None)
        if not (start_date and end_date):
            dt_curr = datetime.now()
            dt_prev = dt_curr - timedelta(hours=1)
            start_date = dt_prev.isoformat()
            end_date = dt_curr.isoformat()
        params.start_date = start_date
        params.end_date = end_date

        status_code, msg = user_actions_dset(params, size)
    return {"statusCode": status_code, "body": json.dumps(msg)}
