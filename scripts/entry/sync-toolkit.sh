#!/usr/bin/env bash

set -o xtrace
set -o errexit

# We allow the use of undefined variables, otherwise, some scripts will not work.
# set -o nounset

TOOLKIT_DIR="$HOME/code/terminal-toolkit"

sync() {
    cd $TOOLKIT_DIR

    echo "start synchronizing..."

    # Check if there are uncommitted changes.
    #
    # reference:
    # https://stackoverflow.com/questions/3878624/how-do-i-programmatically-determine-if-there-are-uncommitted-changes
    #
    # Check the exit status of the command
    if ! git diff-index --quiet HEAD --; then
        echo "workspace unclean, commit staff..."
        git add --all
        git commit -m "update"
    fi

    git config pull.rebase false # merge (the default strategy)
    git pull

    git push
}

update_bin() {
    BINARY_DIR="$HOME"/bin

    # Create bin directory if not exist.
    [[ -d "$BINARY_DIR" ]] || mkdir "$BINARY_DIR"

    # Add "sync-toolkit" command, used to synchronize the toolkit.
    ln -sf $TOOLKIT_DIR/scripts/entry/sync-toolkit.sh "$BINARY_DIR"/sync-toolkit.sh
}

link_rc() {
    # Link the rc file to the home directory.
    ln -sf $TOOLKIT_DIR/scripts/entry/xiaochen-rc.sh "$HOME"/.xiaochen-rc.sh
}

if git config --get user.name &> /dev/null; then
    sync
else
    echo "git user.name not set, skip synchronization..."
fi

link_rc

update_bin
