#!/usr/bin/env bash

# ========================================
# Usage
# ========================================

# wget --no-cache  -O - https://raw.githubusercontent.com/XiaochenCui/terminal-toolkit/main/scripts/vm/mount-disk.sh | bash

set -o xtrace
set -o errexit
set -o nounset
set -o pipefail

DISK_PATH=/dev/sdb
MOUNT_PATH=/mnt/disks/medium

# exit if the disk is already mounted
if mount | grep $DISK_PATH; then
  echo "The disk is already mounted."
  exit 0
fi

# This step will erase all data on the disk!
# 
# format the disk
# 
# sudo mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard $DISK_PATH

# mount the disk
sudo mkdir -p $MOUNT_PATH
sudo mount -o discard,defaults $DISK_PATH $MOUNT_PATH
sudo chmod a+w $MOUNT_PATH