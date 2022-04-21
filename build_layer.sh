#!/usr/bin/env bash

# NumPy 1.21.5
NUMPY="https://files.pythonhosted.org/packages/f8/cc/038b8277fe977ae1f18d11660386af6093547d6c0bd9a9fadbed4795091a/numpy-1.21.5-cp39-cp39-manylinux_2_12_x86_64.manylinux2010_x86_64.whl"

rm -f layer.zip

mkdir -p layer/python

cp generator/{data,utils}.py layer/python
cp config/generator_params.json layer

python3 -m venv venv
source venv/bin/activate
pip install --target layer/python Faker==10.0.0
deactivate

cd layer

wget $NUMPY
unzip numpy*.whl -d python

zip -r ../layer.zip python
zip -g ../layer.zip generator_params.json

rm -rf ../layer
