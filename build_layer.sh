#!/usr/bin/env bash

rm -f package.zip

mkdir -p package/python

python3 -m venv venv
source venv/bin/activate
pip install --target package/python -r requirements.txt
deactivate
rm -rf package/python/{*dist-info,__pycache__}

cp generator/{data,utils}.py package/python
cp config/generator_params.json package

zip -r package.zip package

rm -rf package
