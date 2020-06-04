#!/usr/bin/env bash

export PY_VERSION="3.6"
export BASE_DIR="dependencies"
export PKG_DIR="${BASE_DIR}/python"

rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}

docker run --rm -v $(pwd):/foo -w /foo lambci/lambda:build-python3.6 \
    pip install -r requirements.txt --no-deps -t ${PKG_DIR}
    touch ${PKG_DIR}/__init__.py
    cp ../../models/*.py ${PKG_DIR}