#!/usr/bin/env bash

export PKG_DIR="python"

sudo rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}

docker run --rm -v $(pwd):/foo -w /foo lambci/lambda:build-python3.6 \
    pip install -r requirements.txt --no-deps -t ${PKG_DIR}
    cp ../../models/*.py ${PKG_DIR}