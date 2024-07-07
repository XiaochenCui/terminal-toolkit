#!/usr/bin/env bash

# wget -O - https://raw.githubusercontent.com/XiaochenCui/terminal-toolkit/main/scripts/install/ubuntu.sh | bash

set -o xtrace
set -o errexit
set -o nounset
set -o pipefail

sudo apt-get update -y

# install zsh
# sudo apt-get install -y zsh

# install oh-my-zsh
# sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# install tmux
sudo apt-get install -y tmux

WORKSPACE=$HOME/code
mkdir -p $WORKSPACE

cd $WORKSPACE
git clone --depth=1 https://github.com/XiaochenCui/terminal-toolkit.git 

XIAOCHEN_RC="$HOME"/code/terminal-toolkit/scripts/entry/xiaochen-rc

# insert xiaochen-rc to .zshrc
if ! grep -q "$XIAOCHEN_RC" "$HOME"/.zshrc; then
  echo "source $XIAOCHEN_RC" >> "$HOME"/.zshrc
fi

source $XIAOCHEN_RC