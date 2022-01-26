# setup.py
# Setup installation for the application.

from pathlib import Path

from setuptools import setup

BASE_DIR = Path(__file__).parent

with open(Path(BASE_DIR, "requirements.txt")) as file:
    required_packages = [ln.strip() for ln in file.readlines()]

test_packages = ["typer==0.4.0"]

dev_packages = ["black==21.12b0", "flake8==4.0.1", "isort==5.10.1"]


setup(
    version="0.1",
    author="Dmytro Shurko",
    python_requires=">=3.6",
    install_requires=[required_packages],
    extras_require={
        "test": test_packages,
        "dev": test_packages + dev_packages,
    },
    entry_points={
        "console_scripts": [
            "generate = generator.main:app",
        ]
    },
)
