set shell := ['fish', '-c']

default:
    just --list

uv-init-dir:
    uv venv
    source .venv/bin/activate.fish
    uv pip install -r requirements.txt

update:
    ./scripts/update.sh