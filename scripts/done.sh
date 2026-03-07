#!/bin/bash

set -e

branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$branch" = "main" ]; then
    echo "== already on main"
    exit 1
fi

git checkout main
git pull # sync with remote after merging PR
git branch -d $branch

echo "== merged and cleaned up: $branch"
echo "== start your next feature with: ./scripts/feature.sh"