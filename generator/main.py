# generator/main.py

from argparse import Namespace
from pathlib import Path

import typer

from config import config
from generator import data, utils

app = typer.Typer()


@app.command()
def user_ids(
    data_fp: Path = Path(config.DATA_DIR, "user_ids.json"), size: int = 1000
) -> None:
    user_ids = data.generate_user_ids(size)
    utils.save_data(user_ids, data_fp)


@app.command()
def items(
    data_fp: Path = Path(config.DATA_DIR, "items.json"),
    size: int = 1000,
    params_fp: Path = Path(config.CONFIG_DIR, "generator_params.json"),
):
    params = Namespace(**utils.load_data(filepath=params_fp))
    items = data.generate_items(params, size)
    utils.save_data(items, data_fp)


@app.command()
def user_actions(
    data_fp: Path = Path(config.DATA_DIR, "user_actions.json"),
    user_ids_fp: Path = Path(config.DATA_DIR, "user_ids.json"),
    items_fp: Path = Path(config.DATA_DIR, "items.json"),
    size: int = 1000,
    params_fp: Path = Path(config.CONFIG_DIR, "generator_params.json"),
):
    params = Namespace(**utils.load_data(filepath=params_fp))

    user_ids = utils.load_data(user_ids_fp)
    items = utils.load_data(items_fp)
    items_ids = [item["id"] for item in items]

    user_actions = data.generate_user_actions(
        params, user_ids, items_ids, size
    )
    utils.save_data(user_actions, data_fp)


@app.command()
def user_ids_s3(
    size: int = 1000,
    aws_config_fp: Path = Path(config.CONFIG_DIR, "aws_config.json"),
):
    user_ids = data.generate_user_ids(size)

    aws_config = Namespace(**utils.load_data(filepath=aws_config_fp))
    utils.save_data_s3(aws_config, data=user_ids, dtype="user_ids")


@app.command()
def items_s3(
    size: int = 1000,
    params_fp: Path = Path(config.CONFIG_DIR, "generator_params.json"),
    aws_config_fp: Path = Path(config.CONFIG_DIR, "aws_config.json"),
):
    params = Namespace(**utils.load_data(filepath=params_fp))
    items = data.generate_items(params, size)

    aws_config = Namespace(**utils.load_data(filepath=aws_config_fp))
    utils.save_data_s3(aws_config, data=items, dtype="item")
