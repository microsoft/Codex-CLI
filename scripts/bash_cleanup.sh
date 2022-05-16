#!/usr/bin/env bash

uninstall()
{
    # Remove the script sourced by .bashrc
    rm -f $HOME/.openairc

    # Remove credentials and other personal settings
    local BASH_NL_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )/"
    echo -n > $BASH_NL_PATH/src/openaiapirc

    # Remove key binding (works only for sourced script calls)
    if [ $SOURCED -eq 1 ]; then
        bind -r "\C-g"
    fi

    echo "Codex CLI has been removed."
}

# Detect if the script is sourced
(return 0 2>/dev/null) && SOURCED=1 || SOURCED=0

uninstall

unset SOURCED
