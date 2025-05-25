#!/usr/bin/env bash
set -euo pipefail

# Check for network connectivity by attempting to reach the npm registry.
# Returns 0 if the network is reachable, 1 otherwise. Any failure in the
# network check should not terminate the script when `set -e` is enabled.
check_network() {
  curl -s --head https://registry.npmjs.org >/dev/null 2>&1 && return 0 || return 1
}

if check_network; then
  network_available=true
else
  network_available=false
fi

# Change to repository root if script is run from elsewhere
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

# Copy example environment files if they don't already exist
cp -n .env.example .env.local 2>/dev/null || true
cp -n backend/.env.example backend/.env 2>/dev/null || true

# Install Node.js dependencies if network is available
if [ "$network_available" = true ]; then
  echo "Installing Node.js dependencies..."
  npm ci
  cd frontend && npm ci && cd ..
else
  echo "Network unavailable, skipping Node.js dependency installation." >&2
fi

# Set up Python virtual environment and install backend dependencies
python3 -m venv .venv

if [ "$network_available" = true ]; then
  echo "Installing Python dependencies..."
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r backend/requirements.txt
  deactivate
else
  echo "Network unavailable, skipping Python dependency installation." >&2
fi
