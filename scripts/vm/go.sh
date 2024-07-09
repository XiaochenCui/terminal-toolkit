#!/usr/bin/env bash

# ========================================
# Usage
# ========================================

# wget --no-cache -O - https://raw.githubusercontent.com/XiaochenCui/terminal-toolkit/main/scripts/vm/go.sh | bash

# ========================================
# Bash Options
# ========================================

set -o xtrace
set -o errexit
set -o nounset
set -o pipefail

# ========================================
# Init workspace
# ========================================

WORKSPACE=/mnt/disks/medium

CODE_DIR=/mnt/disks/medium/code
mkdir -p $CODE_DIR

LIB_DIR=/mnt/disks/medium/lib
mkdir -p $LIB_DIR

BIN_DIR=/mnt/disks/medium/bin
mkdir -p $BIN_DIR

# ========================================
# Install Go (1.22.5)
# ========================================

cd $BIN_DIR

wget https://golang.org/dl/go1.22.5.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.22.5.linux-amd64.tar.gz

# ========================================
# Install Go (1.
# ========================================