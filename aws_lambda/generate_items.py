import json
from argparse import Namespace

import boto3
import data
import utils

params_fp = "/opt/generator_params.json"

lambda_client = boto3.client("lambda")


def items_dset(
    params: Namespace, size: int = 1000, n_del: int = 5, dt: str = None
):
    try:
        items = data.generate_items(params, size)
    except AttributeError:
        return 400, "Some parameters are incorrect or missing."
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Data wasn't generated."

    try:
        base_path = utils.dt_path("items", dt)
        utils.save_data_s3(items, base_path + ".json")
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Data wasn't saved to S3."

    new_available = [item["id"] for item in items]

    request_body = {"n_del": n_del, "new_available": new_available, "dt": dt}
    invoke_response = lambda_client.invoke(
        FunctionName="delete_items",
        InvocationType="RequestResponse",
        Payload=json.dumps({"body": json.dumps(request_body)}),
    )
    response = json.load(invoke_response["Payload"])
    status_code = response["statusCode"]
    body = response["body"]

    if status_code != 200:
        return status_code, f"Data wasn't deleted. {body}"
    else:
        return 200, f"{size} items generated, {n_del} items deleted."


def lambda_handler(event, context):
    if not event["body"]:
        status_code, msg = 400, "Parameters not provided."
    else:
        size = body.get("size", 100)
        n_del = body.get("n_del", 5)
        dt = body.get("dt", None)
        if "params" in body:
            params = Namespace(**body["params"])
        else:
            params = Namespace(**utils.load_data(filepath=params_fp))
        status_code, msg = items_dset(params, size, n_del, dt)
    return {"statusCode": status_code, "body": json.dumps(msg)}
