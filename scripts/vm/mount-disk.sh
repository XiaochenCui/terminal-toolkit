#!/usr/bin/env bash

# wget -O - https://raw.githubusercontent.com/XiaochenCui/terminal-toolkit/main/scripts/vm/mount-disk.sh | bash

set -o xtrace
set -o errexit
set -o nounset
set -o pipefail

DISK_PATH=/dev/sdb
MOUNT_PATH=/mnt/disks/medium

# format the disk
sudo mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard $DISK_PATH

# mount the disk
sudo mkdir -p $MOUNT_PATH
sudo mount -o discard,defaults $DISK_PATH $MOUNT_PATH
sudo chmod a+w $MOUNT_PATH