#!/usr/bin/env bash

echo "Run pylava"
#find -name '*.py' | xargs pylava --options setup.cfg --format pep8

echo "Run mypy"
readonly python_files=$(find -name '*.py')

for f in $python_files; do
    mypy --config-file setup.cfg $f
done

