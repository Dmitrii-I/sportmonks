#!/usr/bin/env bash

echo "Run pylava"
find -name '*.py' | xargs pylava --options setup.cfg --format pep8

echo "Run mypy"
find -name '*.py' | xargs mypy

