#!/bin/bash
# Xianyu Auto-Reply Service Startup Script
# Managed by launchd — ai.openclaw.xianyu

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv"
ENV_FILE="/Users/henry/.openclaw/.env.xianyu"

# Load environment variables from .env.xianyu if it exists
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
fi

# Activate Python virtual environment
source "$VENV_DIR/bin/activate"

# Change to project directory
cd "$PROJECT_DIR"

# Execute the service
exec python Start.py
