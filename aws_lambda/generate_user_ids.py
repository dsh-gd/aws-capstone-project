import json

import data
import utils


def user_ids_dset(size: int):
    try:
        user_ids = data.generate_user_ids(size)
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Data wasn't generated."
    try:
        path = utils.dt_path("user_ids") + ".json"
        utils.save_data_s3(user_ids, path)
    except:  # NOQA: E722 (do not use bare 'except')
        return 500, "Data wasn't saved to S3."
    return 201, f"{size} user IDs generated."


def lambda_handler(event, context):
    if not event["body"]:
        status_code, msg = 400, "Parameters not provided."
    else:
        body = json.loads(event["body"])
        size = body.get("size", 100)
        status_code, msg = user_ids_dset(size)
    return {"statusCode": status_code, "body": json.dumps(msg)}
