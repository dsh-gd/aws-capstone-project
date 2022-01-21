from argparse import Namespace

from generator import data, utils


def user_ids_dset(aws_config: Namespace, size: int = 1000) -> None:
    user_ids = data.generate_user_ids(size)
    path = utils.dt_path("user_ids") + ".json"
    utils.save_data_s3(aws_config, data=user_ids, path=path)


def items_dset(
    aws_config: Namespace, params: Namespace, size: int = 1000, n_del: int = 5
) -> None:
    dset_type = "items"
    lst_base_path = utils.latest_dset_path(aws_config, dset_type)

    if lst_base_path:
        lst_available = set(
            utils.load_data_s3(aws_config, lst_base_path + "_available.json")
        )
        lst_unavailable = utils.load_data_s3(
            aws_config, lst_base_path + "_unavailable.json"
        )
    else:
        lst_available = set()
        lst_unavailable = []

    delete = utils.to_delete(lst_available, n_del=3)
    leave = lst_available - delete

    items = data.generate_items(params, size)

    base_path = utils.dt_path(dset_type)
    utils.save_data_s3(aws_config, data=items, path=base_path + ".json")

    new_available = [item["id"] for item in items]
    new_available.extend(leave)
    utils.save_data_s3(
        aws_config, data=new_available, path=base_path + "_available.json"
    )

    lst_unavailable.extend(delete)
    utils.save_data_s3(
        aws_config, data=lst_unavailable, path=base_path + "_unavailable.json"
    )


def user_actions_dset(
    aws_config: Namespace, params: Namespace, size: int = 1000
) -> None:
    user_ids_base_path = utils.latest_dset_path(
        aws_config, dset_type="user_ids"
    )
    user_ids = utils.load_data_s3(aws_config, user_ids_base_path + ".json")

    items_base_path = utils.latest_dset_path(aws_config, dset_type="items")
    items_ids = utils.load_data_s3(
        aws_config, items_base_path + "_available.json"
    )

    user_actions = data.generate_user_actions(
        params, user_ids, items_ids, size
    )
    path = utils.dt_path("user_actions") + ".json"
    utils.save_data_s3(aws_config, data=user_actions, path=path)
