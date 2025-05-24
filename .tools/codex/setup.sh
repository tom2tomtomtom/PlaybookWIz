#!/usr/bin/env bash
set -euo pipefail

# Change to repository root if script is run from elsewhere
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

# Copy example environment files if they don't already exist
cp -n .env.example .env.local 2>/dev/null || true
cp -n backend/.env.example backend/.env 2>/dev/null || true

# Install Node.js dependencies
npm ci
cd frontend && npm ci && cd ..

# Set up Python virtual environment and install backend dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
deactivate
