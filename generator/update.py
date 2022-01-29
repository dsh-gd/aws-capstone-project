# generator/update.py
# Functions for updating data sets.

from argparse import Namespace

from generator import data, utils


def user_ids_dset(size: int = 1000) -> None:
    user_ids = data.generate_user_ids(size)
    path = utils.dt_path("user_ids") + ".json"
    utils.save_data_s3(user_ids, path)


def delete_items(
    n_del: int = 5,
    new_available: list = [],
    dt: str = None,
) -> None:
    dset_prefix = "items"
    base_lst_path = utils.latest_path(dset_prefix, "_available", dt)

    if base_lst_path:
        available = set(utils.load_data_s3(base_lst_path + "_available.json"))
    else:
        available = set()

    delete = utils.to_delete(available, n_del)
    leave = available - delete

    base_path = utils.dt_path(dset_prefix, dt)
    utils.save_data_s3(
        list(leave) + new_available, base_path + "_available.json"
    )
    utils.save_data_s3(list(delete), base_path + "_unavailable.json")


def items_dset(
    params: Namespace,
    size: int = 1000,
    n_del: int = 5,
    dt: str = None,
) -> None:
    items = data.generate_items(params, size)

    base_path = utils.dt_path("items", dt)
    utils.save_data_s3(items, base_path + ".json")

    new_available = [item["id"] for item in items]
    delete_items(n_del, new_available, dt)


def user_actions_dset(params: Namespace, size: int = 1000) -> None:
    user_ids_path = utils.latest_path("user_ids") + ".json"
    user_ids = utils.load_data_s3(path=user_ids_path)

    base_items_path = utils.latest_path(
        dset_prefix="items", dset_type="_available"
    )
    items_path = base_items_path + "_available.json"
    items_ids = utils.load_data_s3(path=items_path)

    user_actions = data.generate_user_actions(
        params, user_ids, items_ids, size
    )
    path = utils.dt_path("user_actions") + ".json"
    utils.save_data_s3(data=user_actions, path=path)
