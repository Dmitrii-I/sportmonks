#!/usr/bin/env bash

echo "Run pylava"
#find -name '*.py' | xargs pylava --options setup.cfg --format pep8

echo "Run mypy"

for f in sportmonks_v2/*.py; do
    echo Check file "$f"
    mypy --config-file setup.cfg "$f"
done