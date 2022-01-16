# generator/main.py

from argparse import Namespace
from pathlib import Path

import typer

from config import config
from generator import data, utils

app = typer.Typer()


@app.command()
def users_ids(
    data_fp: Path = Path(config.DATA_DIR, "users_ids.json"), size: int = 1000
) -> None:
    users_ids = data.generate_users_ids(size)
    utils.save_data(users_ids, data_fp)


@app.command()
def items(
    data_fp: Path = Path(config.DATA_DIR, "items.json"),
    size: int = 1000,
    params_fp: Path = Path(config.CONFIG_DIR, "params.json"),
):
    params = Namespace(**utils.load_data(filepath=params_fp))
    items = data.generate_items(params, size)
    utils.save_data(items, data_fp)


@app.command()
def user_actions(
    data_fp: Path = Path(config.DATA_DIR, "user_actions.json"),
    users_ids_fp: Path = Path(config.DATA_DIR, "users_ids.json"),
    items_fp: Path = Path(config.DATA_DIR, "items.json"),
    size: int = 1000,
    params_fp: Path = Path(config.CONFIG_DIR, "params.json"),
):
    params = Namespace(**utils.load_data(filepath=params_fp))

    users_ids = utils.load_data(users_ids_fp)
    items = utils.load_data(items_fp)
    items_ids = [item["id"] for item in items]

    user_actions = data.generate_user_actions(
        params, users_ids, items_ids, size
    )
    utils.save_data(user_actions, data_fp)
