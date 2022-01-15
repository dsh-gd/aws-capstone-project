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
    params_fp: Path = Path(config.CONFIG_DIR, "params.json"),
):
    params = Namespace(**utils.load_data(filepath=params_fp))
    items = data.generate_items(params, size)
    utils.save_data(items, data_fp)
