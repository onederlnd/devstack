#!/bin/bash
# bash ./script/ship.sh
set -e # stop on any error

# activate virtual environment
. .venv/bin/activate

# prevent accidental push from wrong branch
branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$branch" != "main" ]; then
    echo "== not on main branch (currently on '$branch')"
    exit 1
fi

echo "== running tests..."
pytest tests/ -v

echo "== linting..."
flake8 app/ --max-line-length=100 --ignore=E501,W503

echo " == staging changes..."
git add .
git status

echo ""
read -p "commit message: " msg

if [ -z "$msg" ]; then
    echo "== commit message required"
    exit 1
fi

git commit -m "$msg"
git push

echo "== shipped!"

