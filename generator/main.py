# generator/main.py
# CLI application

from argparse import Namespace
from pathlib import Path

import typer

from config import config
from generator import update, utils

app = typer.Typer()


@app.command()
def user_ids(
    aws_config_fp: Path = Path(config.CONFIG_DIR, "aws_config.json"),
    size: int = 1000,
):
    aws_config = Namespace(**utils.load_data(filepath=aws_config_fp))
    update.user_ids_dset(aws_config, size)


@app.command()
def items(
    aws_config_fp: Path = Path(config.CONFIG_DIR, "aws_config.json"),
    params_fp: Path = Path(config.CONFIG_DIR, "generator_params.json"),
    size: int = 1000,
    n_del: int = 5,
):
    aws_config = Namespace(**utils.load_data(filepath=aws_config_fp))
    params = Namespace(**utils.load_data(filepath=params_fp))
    update.items_dset(aws_config, params, size, n_del)


@app.command()
def user_actions(
    aws_config_fp: Path = Path(config.CONFIG_DIR, "aws_config.json"),
    params_fp: Path = Path(config.CONFIG_DIR, "generator_params.json"),
    size: int = 1000,
):
    aws_config = Namespace(**utils.load_data(filepath=aws_config_fp))
    params = Namespace(**utils.load_data(filepath=params_fp))
    update.user_actions_dset(aws_config, params, size)
