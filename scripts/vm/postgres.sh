#!/usr/bin/env bash

# ========================================
# Usage
# ========================================

# wget --no-cache -O - https://raw.githubusercontent.com/XiaochenCui/terminal-toolkit/main/scripts/vm/postgres.sh | bash

# ========================================
# Bash Options
# ========================================

set -o xtrace
set -o errexit
set -o nounset
set -o pipefail

# ========================================
# Install Postgres
# ========================================

sudo apt -y update
sudo apt -y install postgresql postgis