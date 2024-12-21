export PATH=$HOME/bin:$PATH

general() {
    # enable UTF-8 support
    # 
    # reference:
    # https://unix.stackexchange.com/questions/303712/how-can-i-enable-utf-8-support-in-the-linux-console
    export LC_ALL=en_US.UTF-8
    export LANG=en_US.UTF-8
    export LANGUAGE=en_US.UTF-8

    # Add "z" command, used to quickly jump to the directory.
    source "$HOME"/code/terminal-toolkit/scripts/entry/z.sh

    # Active alias
    source "$HOME"/code/terminal-toolkit/scripts/entry/alias.sh

    # Add binary path: golang
    export PATH=$PATH:/usr/local/go/bin

    # Add binary path: golang bianries ("go install" will install binaries to $HOME/go/bin)
    export PATH=$PATH:$HOME/go/bin

    # Add binary path: ~/bin, which is used to store some custom scripts
    export PATH=$PATH:$HOME/bin

    # Set the default editor to vim.
    export EDITOR=vim
    export VISUAL=vim

    # Update the PYTHONPATH, NB: don't use "~" in the path since it will not be expanded.
    export PYTHONPATH="$HOME/code/terminal-toolkit/scripts/:$PYTHONPATH"
}

# The function name should not conflict with any command.
xiaochen_zsh() {
    # https://github.com/dvorka/hstr/blob/master/CONFIGURATION.md
    export HSTR_CONFIG=hicolor,keywords-matching,raw-history-view,prompt-bottom

    # zsh prompt config
    # ret_status="%(?:%{$fg_bold[green]%}🍚 :%{$fg_bold[red]%}🍔 )"
    # PROMPT='${ret_status} %{$fg[cyan]%}%c%{$reset_color%} $(git_prompt_info)'
}

# The function name should not conflict with any command.
xiaochen_bash() {
    # we cannot leave the function empty, otherwise it will throw an error
    true
}

general

case $SHELL in
"/bin/zsh")
    xiaochen_zsh
    ;;
"/usr/bin/zsh")
    xiaochen_zsh
    ;;
"/bin/bash")
    xiaochen_bash
    ;;
esac