#!/usr/bin/env bash

set -o xtrace
set -o errexit
set -o nounset
set -o pipefail

WORKSPACE=$HOME/code
mkdir -p $WORKSPACE

cd $WORKSPACE
rm -rf cockroach
git clone --recurse-submodules --depth 1 --branch debug https://github.com/XiaochenCui/cockroach.git

cd $WORKSPACE/cockroach
touch .bazelrc.user
echo 'build --config=dev' >> .bazelrc.user
echo 'build --config=lintonbuild' >> .bazelrc.user
echo 'test --test_tmpdir=/tmp/cockroach' >> .bazelrc.user
echo 'build --remote_cache=http://127.0.0.1:9867' >> .bazelrc.user

cd $WORKSPACE
wget https://github.com/bazelbuild/bazelisk/releases/download/v1.20.0/bazelisk-linux-amd64
chmod +x bazelisk-linux-amd64
sudo ln -sf $WORKSPACE/bazelisk-linux-amd64 /usr/local/bin/bazel

cd $WORKSPACE/cockroach
./dev doctor
bazel clean --expunge
./dev generate
./dev lint
./dev test