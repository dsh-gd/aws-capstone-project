# generator/update.py
# Functions for updating data sets.

from argparse import Namespace

from generator import data, utils


def user_ids_dset(aws_config: Namespace, size: int = 1000) -> None:
    user_ids = data.generate_user_ids(size)
    path = utils.dt_path("user_ids") + ".json"
    utils.save_data_s3(aws_config, user_ids, path)


def delete_items(
    aws_config: Namespace, n_del: int = 5, new_available: list = []
) -> None:
    dset_prefix = "items"
    base_lst_path = utils.latest_path(aws_config, dset_prefix, "_available")

    if base_lst_path:
        available = set(
            utils.load_data_s3(aws_config, base_lst_path + "_available.json")
        )
    else:
        available = set()

    delete = utils.to_delete(available, n_del)
    leave = available - delete

    base_path = utils.dt_path(dset_prefix)
    utils.save_data_s3(
        aws_config, list(leave) + new_available, base_path + "_available.json"
    )
    utils.save_data_s3(
        aws_config, list(delete), base_path + "_unavailable.json"
    )


def items_dset(
    aws_config: Namespace, params: Namespace, size: int = 1000, n_del: int = 5
) -> None:
    items = data.generate_items(params, size)

    path = utils.dt_path("items") + ".json"
    utils.save_data_s3(aws_config, items, path)

    new_available = [item["id"] for item in items]
    delete_items(aws_config, n_del, new_available)


def user_actions_dset(
    aws_config: Namespace, params: Namespace, size: int = 1000
) -> None:
    user_ids_path = utils.latest_path(aws_config, "user_ids") + ".json"
    user_ids = utils.load_data_s3(aws_config, path=user_ids_path)

    base_items_path = utils.latest_path(
        aws_config, dset_prefix="items", dset_type="_available"
    )
    items_path = base_items_path + "_available.json"
    items_ids = utils.load_data_s3(aws_config, path=items_path)

    user_actions = data.generate_user_actions(
        params, user_ids, items_ids, size
    )
    path = utils.dt_path("user_actions") + ".json"
    utils.save_data_s3(aws_config, data=user_actions, path=path)
