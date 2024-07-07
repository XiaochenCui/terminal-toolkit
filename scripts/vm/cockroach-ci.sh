#!/usr/bin/env bash

# wget -O - https://raw.githubusercontent.com/XiaochenCui/terminal-toolkit/main/scripts/vm/cockroach-ci.sh | bash

set -o xtrace
set -o errexit
set -o nounset
set -o pipefail

WORKSPACE=/mnt/disks/medium/code
mkdir -p $WORKSPACE

cd $WORKSPACE
wget https://github.com/bazelbuild/bazelisk/releases/download/v1.20.0/bazelisk-linux-amd64
chmod +x bazelisk-linux-amd64
sudo ln -sf $WORKSPACE/bazelisk-linux-amd64 /usr/local/bin/bazel

sudo apt-get update -y
sudo apt-get install -y gcc
sudo apt-get install -y cmake

# https://stackoverflow.com/questions/73529401/cannot-execute-cc1plus-execvp-no-such-file-or-directory
# handle the error: "cannot execute cc1plus: execvp: No such file or directory"
sudo apt-get install -y --reinstall g++-13-x86-64-linux-gnu

cd $WORKSPACE
rm -rf resolv_wrapper
git clone https://git.samba.org/resolv_wrapper.git

cd $WORKSPACE/resolv_wrapper
mkdir build
cd build
LIB_DIR=$HOME/local/libresolv_wrapper
mkdir -p $LIB_DIR
cmake -DCMAKE_INSTALL_PREFIX=$LIB_DIR ..
make
make install

echo "$LIB_DIR/lib" | sudo tee /etc/ld.so.conf.d/local.conf
sudo ldconfig
ldconfig -p | grep resolv_wrapper

# If the gcc use "ld.gold" as the linker, if may doesn't work with ldconfig.
# So we need to copy the library to /usr/lib manually.
#
# UPDATE: the following approaches don't work.
# sudo cp $LIB_DIR/lib/* /usr/lib/
# sudo cp -r ~/local/libresolv_wrapper/lib/* /usr/lib

cd $WORKSPACE
rm -rf cockroach
git clone --recurse-submodules --depth 1 --branch debug https://github.com/XiaochenCui/cockroach.git

cd $WORKSPACE/cockroach
touch .bazelrc.user
echo 'build --config=dev' >> .bazelrc.user
echo 'build --config=lintonbuild' >> .bazelrc.user
echo 'test --test_tmpdir=/tmp/cockroach' >> .bazelrc.user
echo 'build --remote_cache=http://127.0.0.1:9867' >> .bazelrc.user

cd $WORKSPACE/cockroach
./dev doctor
bazel clean --expunge
./dev generate
./dev lint
./dev test