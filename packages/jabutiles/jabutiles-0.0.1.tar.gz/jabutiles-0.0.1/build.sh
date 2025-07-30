#! /usr/bin/bash

echo "build"
python -m build

echo "upload"
twine upload -r testpypi dist/* --skip-existing
