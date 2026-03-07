#!/bin/bash
set -e

read -p "feature name (e.g. user-following): " name

if [ -z "$name" ]; then
    echo "== feature name required"
    exit 1
fi

git checkout main
git pull
git checkout -b feat/$name

cp NOTES-template.md NOTES.md
echo "== created and switched to branch: feat/$name"
echo "== NOTES.md created - fill it in before writing code"