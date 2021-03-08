#!/usr/bin/env bash

export BASE_DIR="dependencies"
export PKG_DIR="${BASE_DIR}/python"

rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}

python3.6 -m pip install -r requirements.txt --no-deps -t ${PKG_DIR}
touch ${PKG_DIR}/__init__.py
cp ../../auth/*.py ${PKG_DIR}