#!/usr/bin/env sh

set -eu

MESSAGE_FILE="$1"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../../.." && pwd)

sh "$REPO_ROOT/scripts/check_commit_message.sh" "$MESSAGE_FILE"
