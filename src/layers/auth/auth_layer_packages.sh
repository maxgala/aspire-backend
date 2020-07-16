#!/usr/bin/env bash

export PY_VERSION="3.6"
export BASE_DIR="dependencies"
export PKG_DIR="${BASE_DIR}/python"

rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}

python${PY_VERSION} -m pip install -r requirements.txt --no-deps -t ${PKG_DIR}
touch ${PKG_DIR}/__init__.py
cp ../../auth/*.py ${PKG_DIR}