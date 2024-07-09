#!/usr/bin/env bash

# ========================================
# Usage
# ========================================

# wget --no-cache -O - https://raw.githubusercontent.com/XiaochenCui/terminal-toolkit/main/scripts/vm/cockroach-ci.sh | bash

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

WORKSPACE=$HOME

CODE_DIR=$WORKSPACE/code
mkdir -p $CODE_DIR

LIB_DIR=$WORKSPACE/lib
mkdir -p $LIB_DIR

BIN_DIR=$WORKSPACE/bin
mkdir -p $BIN_DIR

# ========================================
# Install "bazeliisk" as "bazel"
# ========================================

cd $BIN_DIR
wget https://github.com/bazelbuild/bazelisk/releases/download/v1.20.0/bazelisk-linux-amd64
chmod +x bazelisk-linux-amd64
sudo ln -sf $BIN_DIR/bazelisk-linux-amd64 /usr/local/bin/bazel

# ========================================
# Install dependencies
# ========================================

sudo apt-get update -y

sudo apt-get install -y gcc g++

# "patchelf" is required use "crosslinux" config in bazel
sudo apt-get install -y patchelf

# ========================================
# Install library "resolv_wrapper"
# ========================================

# sudo apt install -y libresolv-wrapper

# The following code are kept to remind how much effort I have put to install "resolv_wrapper" manually and failed.

# cd $WORKSPACE
# rm -rf resolv_wrapper
# git clone https://git.samba.org/resolv_wrapper.git

# cd $WORKSPACE/resolv_wrapper
# mkdir build
# cd build
# LIB_RESOLV_WRAPPER=$LIB_DIR/libresolv_wrapper
# mkdir -p $LIB_RESOLV_WRAPPER
# cmake -DCMAKE_INSTALL_PREFIX=$LIB_RESOLV_WRAPPER ..
# make
# make install

# echo "$LIB_RESOLV_WRAPPER/lib" | sudo tee /etc/ld.so.conf.d/local.conf
# sudo ldconfig
# ldconfig -p | grep resolv_wrapper

# ========================================
# init cockroach
# ========================================

# only do the following steps if the cockroach repo is not cloned
if [ ! -d "$CODE_DIR/cockroach" ]; then
    cd $CODE_DIR
    rm -rf cockroach
    git clone --recurse-submodules --depth 1 --branch debug https://github.com/XiaochenCui/cockroach.git

    cd $CODE_DIR/cockroach
    touch .bazelrc.user

    # Use "crosslinux" instead of "def" to avoid error.
    # 
    # https://github.com/cockroachdb/cockroach/issues/110799#issuecomment-1731990917
    echo 'build --config=crosslinux' >>.bazelrc.user

    echo 'build --config=lintonbuild' >>.bazelrc.user
    echo 'test --test_tmpdir=/tmp/cockroach' >>.bazelrc.user
    echo 'build --remote_cache=http://127.0.0.1:9867' >>.bazelrc.user
fi

# ========================================
# test cockroach
# ========================================

cd $CODE_DIR/cockroach
./dev doctor
bazel clean --expunge
./dev gen
./dev lint
./dev test
./dev build
