#/usr/bin/env bash
set -euo pipefail

GENERATOR='scripts/generator.py'
OUT_FILE='src/llmpy-models/enum.py'
TEMP_FILE='enum.tmp.py'
TOML='pyproject.toml'

# source virtual env
source .venv/bin/activate

# run enum generator
python "$GENERATOR" > "$TEMP_FILE"

# update if diff from current version
if diff -q "$OUT_FILE" "$TEMP_FILE" >/dev/null; then
    rm "$TEMP_FILE"
    exit 0
fi

mv "$TEMP_FILE" "$OUT_FILE"

# update version
VERSION=... # TODO fix

# build and upload
python -m build
twine upload dist/* # TODO check if auth needed