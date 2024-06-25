#!/usr/bin/env bash

set -o xtrace
set -o errexit
set -o nounset
set -o pipefail

WORKSPACE=$HOME/code
mkdir -p $WORKSPACE

cd $WORKSPACE
wget https://github.com/bazelbuild/bazelisk/releases/download/v1.20.0/bazelisk-linux-amd64
chmod +x bazelisk-linux-amd64
sudo ln -sf $WORKSPACE/bazelisk-linux-amd64 /usr/local/bin/bazel
sudo apt-get install -y gcc

# https://stackoverflow.com/questions/73529401/cannot-execute-cc1plus-execvp-no-such-file-or-directory
sudo apt-get install -y --reinstall g++-13-x86-64-linux-gnu

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