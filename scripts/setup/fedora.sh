# Note: we don't use shebang in this script because we want to run it in the current shell environment.

# ========================================
# Prerequisite (must be executed manually)
# ========================================

# # install zsh
# sudo dnf install -y zsh

# # install oh-my-zsh
# sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# # change the default shell to zsh
# sudo lchsh $(whoami)

# ========================================
# Usage
# ========================================

# --no-cache: prevent wget from using cache
# wget --no-cache -O - https://raw.githubusercontent.com/XiaochenCui/terminal-toolkit/main/scripts/setup/fedora.sh | zsh

# ========================================
# Bash Options
# ========================================

set -o xtrace
set -o errexit
set -o pipefail

# we allow unset variables for the sick of "z.sh"
# set -o nounset

# ========================================
# DNF update
# ========================================

sudo dnf update -y

# ========================================
# tmux
# ========================================

sudo dnf install -y tmux

# ========================================
# hstr
# ========================================

# install hstr if not exist
if ! hstr --version &>/dev/null; then
  # dnf cannot find hstr
  # sudo dnf install -y hstr

  # ref:
  # https://github.com/dvorka/hstr/blob/master/INSTALLATION.md#build-on-any-linux-distro
  rm -rf ~/hstr
  git clone https://github.com/dvorka/hstr.git ~/hstr
  cd ./hstr/build/tarball && ./tarball-automake.sh && cd ../..
  ./configure && make
  sudo make install

  hstr --show-configuration >>~/.zshrc
fi

# ========================================
# tree, ncdu
# ========================================

sudo dnf install -y tree

# dnf cannot find ncdu
# sudo dnf install -y ncdu

# ========================================
# init workspace
# ========================================

WORKSPACE=$HOME/code
mkdir -p $WORKSPACE

# ========================================
# terminal-toolkit
# ========================================

cd $WORKSPACE
rm -rf terminal-toolkit
git clone --depth=1 https://github.com/XiaochenCui/terminal-toolkit.git

# ========================================
# activate xiaochen-rc
# ========================================

XIAOCHEN_RC="$HOME"/.xiaochen-rc.sh

# insert xiaochen-rc to .zshrc
if ! grep -q "$XIAOCHEN_RC" "$HOME"/.zshrc; then
  echo "" >>"$HOME"/.zshrc
  echo "# activate xiaochen-rc" >>"$HOME"/.zshrc
  echo "source $XIAOCHEN_RC" >>"$HOME"/.zshrc
fi

# sync xiaochen-rc
$HOME/code/terminal-toolkit/scripts/entry/sync-toolkit.sh

. $XIAOCHEN_RC
