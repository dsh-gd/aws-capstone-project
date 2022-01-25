# generator/main.py
# CLI application

from argparse import Namespace
from pathlib import Path

import typer

from config import config
from generator import update, utils

app = typer.Typer()


@app.command()
def user_ids(size: int = 1000):
    update.user_ids_dset(size)


@app.command()
def items(
    params_fp: Path = Path(config.CONFIG_DIR, "generator_params.json"),
    size: int = 1000,
    n_del: int = 5,
):
    params = Namespace(**utils.load_data(filepath=params_fp))
    update.items_dset(params, size, n_del)


@app.command()
def user_actions(
    params_fp: Path = Path(config.CONFIG_DIR, "generator_params.json"),
    size: int = 1000,
):
    params = Namespace(**utils.load_data(filepath=params_fp))
    update.user_actions_dset(params, size)
