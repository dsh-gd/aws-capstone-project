import json

import utils


def delete_items(n_del: int = 5, new_available: list = [], dt: str = None):
    dset_prefix = "items"
    base_lst_path = utils.latest_path(dset_prefix, "_available", dt)

    if base_lst_path:
        available = set(utils.load_data_s3(base_lst_path + "_available.json"))
    else:
        available = set()

    delete = utils.to_delete(available, n_del)
    leave = available - delete

    try:
        base_path = utils.dt_path(dset_prefix, dt)
        utils.save_data_s3(
            list(leave) + new_available, base_path + "_available.json"
        )
        utils.save_data_s3(list(delete), base_path + "_unavailable.json")
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Data wasn't saved to S3."
    return 200, f"{n_del} items were deleted."


def lambda_handler(event, context):
    if not event["body"]:
        status_code, msg = 400, "Parameters not provided."
    else:
        body = json.loads(event["body"])
        n_del = body.get("n_del", 5)
        new_available = body.get("new_available", [])
        dt = body.get("dt", None)
        status_code, msg = delete_items(n_del, new_available, dt)
    return {"statusCode": status_code, "body": json.dumps(msg)}
