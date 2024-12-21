# Note: we don't use shebang in this script because we want to run it in the current shell environment.

# ========================================
# Prerequisite (must be executed manually)
# ========================================

# # install zsh
# sudo dnf install -y zsh

# # install oh-my-zsh
# sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# ========================================
# Usage
# ========================================

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

sudo dnf install -y hstr

# ========================================
# tree, ncdu
# ========================================

sudo dnf install -y tree ncdu

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

XIAOCHEN_RC="$HOME"/.xiaochen-rc

# insert xiaochen-rc to .zshrc
if ! grep -q "$XIAOCHEN_RC" "$HOME"/.zshrc; then
  echo "" >> "$HOME"/.zshrc
  echo "# activate xiaochen-rc" >> "$HOME"/.zshrc
  echo "source $XIAOCHEN_RC" >> "$HOME"/.zshrc
fi

# sync xiaochen-rc
$HOME/code/terminal-toolkit/scripts/entry/sync-toolkit

. $XIAOCHEN_RC